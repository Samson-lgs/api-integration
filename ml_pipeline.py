"""
Machine Learning Pipeline for AQI Prediction
Includes: Train/Val/Test split, Multiple models, Ensemble stacking, Hyperparameter tuning
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pickle
import json
from pathlib import Path

# Sklearn
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, StackingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# XGBoost
import xgboost as xgb

# Gradient Boosting (alternative to LSTM)
from sklearn.ensemble import GradientBoostingRegressor

# Bayesian Optimization
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import uniform, randint

import warnings
warnings.filterwarnings('ignore')


class AQIPredictionPipeline:
    """
    Complete ML pipeline for AQI prediction with ensemble methods
    """
    
    def __init__(self, target='aqi', random_state=42):
        self.target = target
        self.random_state = random_state
        self.scaler = StandardScaler()
        
        # Models
        self.models = {}
        self.best_params = {}
        self.predictions = {}
        self.metrics = {}
        
        # Ensemble
        self.ensemble_model = None
        
        print("✅ AQI Prediction Pipeline initialized")
    
    def load_data(self, filepath='processed_air_quality_data.csv'):
        """
        Load preprocessed data
        """
        print("\n" + "="*80)
        print("📂 LOADING DATA")
        print("="*80)
        
        self.df = pd.read_csv(filepath)
        self.df['recorded_at'] = pd.to_datetime(self.df['recorded_at'])
        
        print(f"✅ Loaded {len(self.df)} records")
        print(f"   • Shape: {self.df.shape}")
        print(f"   • Date range: {self.df['recorded_at'].min()} to {self.df['recorded_at'].max()}")
        
        return self.df
    
    def select_features(self, feature_set='recommended'):
        """
        Select features for training
        """
        print("\n" + "="*80)
        print("🎯 FEATURE SELECTION")
        print("="*80)
        
        if feature_set == 'minimal':
            # Minimal set for quick training
            features = [
                'pm25', 'pm10', 'no2', 'temperature', 'humidity',
                'hour', 'day_of_week', 'is_weekend'
            ]
        
        elif feature_set == 'recommended':
            # Recommended balanced set
            features = [
                # Core pollutants
                'pm25', 'pm10', 'no2', 'so2', 'co', 'o3',
                
                # Weather
                'temperature', 'humidity', 'wind_speed', 'pressure',
                
                # Temporal
                'hour', 'day_of_week', 'month', 'is_weekend', 'is_rush_hour',
                'hour_sin', 'hour_cos',
                
                # Lag features
                'pm25_lag_1h', 'pm25_lag_3h', 'pm25_lag_24h',
                'temperature_lag_1h',
                
                # Rolling features
                'pm25_rolling_mean_6h', 'pm25_rolling_std_6h',
                'pm25_rolling_mean_24h',
                
                # Derived metrics
                'pm25_pm10_ratio', 'heat_index'
            ]
        
        elif feature_set == 'complete':
            # Use all numeric features
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            features = [col for col in numeric_cols if col != self.target]
            features = [col for col in features if col not in ['year', 'day', 'day_of_year', 'week_of_year']]
        
        else:
            # Custom feature list
            features = feature_set
        
        self.features = features
        print(f"✅ Selected {len(features)} features")
        print(f"   • Feature set: {feature_set if isinstance(feature_set, str) else 'custom'}")
        
        # Show some features
        print(f"\n📋 Sample features:")
        for i, feat in enumerate(features[:10], 1):
            print(f"   {i}. {feat}")
        if len(features) > 10:
            print(f"   ... and {len(features) - 10} more")
        
        return features
    
    def time_series_split(self, train_size=0.7, val_size=0.15, test_size=0.15):
        """
        Split data using time-series-aware sampling (no shuffling!)
        """
        print("\n" + "="*80)
        print("📊 TIME-SERIES AWARE DATA SPLITTING")
        print("="*80)
        
        # Sort by time
        self.df = self.df.sort_values('recorded_at').reset_index(drop=True)
        
        # Remove rows with missing values in features or target
        feature_cols = self.features + [self.target]
        df_clean = self.df[feature_cols].dropna()
        
        print(f"   • Original records: {len(self.df)}")
        print(f"   • After removing NaN: {len(df_clean)}")
        print(f"   • Dropped: {len(self.df) - len(df_clean)} rows")
        
        # Calculate split indices
        n = len(df_clean)
        train_idx = int(n * train_size)
        val_idx = int(n * (train_size + val_size))
        
        # Split data
        X = df_clean[self.features]
        y = df_clean[self.target]
        
        self.X_train = X[:train_idx]
        self.X_val = X[train_idx:val_idx]
        self.X_test = X[val_idx:]
        
        self.y_train = y[:train_idx]
        self.y_val = y[train_idx:val_idx]
        self.y_test = y[val_idx:]
        
        print(f"\n✅ Data Split (Time-Series Aware):")
        print(f"   • Training:   {len(self.X_train):4d} samples ({train_size*100:.1f}%)")
        print(f"   • Validation: {len(self.X_val):4d} samples ({val_size*100:.1f}%)")
        print(f"   • Test:       {len(self.X_test):4d} samples ({test_size*100:.1f}%)")
        print(f"   • Total:      {len(X):4d} samples")
        
        # Scale features
        print(f"\n🔧 Scaling features...")
        self.X_train_scaled = self.scaler.fit_transform(self.X_train)
        self.X_val_scaled = self.scaler.transform(self.X_val)
        self.X_test_scaled = self.scaler.transform(self.X_test)
        
        print(f"✅ Features scaled using StandardScaler")
        
        return self.X_train, self.X_val, self.X_test, self.y_train, self.y_val, self.y_test
    
    def train_linear_regression(self):
        """
        Train Linear Regression model
        """
        print("\n" + "="*80)
        print("📈 TRAINING LINEAR REGRESSION")
        print("="*80)
        
        model = Ridge(alpha=1.0, random_state=self.random_state)
        model.fit(self.X_train_scaled, self.y_train)
        
        # Predictions
        y_pred_train = model.predict(self.X_train_scaled)
        y_pred_val = model.predict(self.X_val_scaled)
        y_pred_test = model.predict(self.X_test_scaled)
        
        # Metrics
        metrics = {
            'train': self._calculate_metrics(self.y_train, y_pred_train),
            'val': self._calculate_metrics(self.y_val, y_pred_val),
            'test': self._calculate_metrics(self.y_test, y_pred_test)
        }
        
        self.models['linear_regression'] = model
        self.predictions['linear_regression'] = {
            'train': y_pred_train,
            'val': y_pred_val,
            'test': y_pred_test
        }
        self.metrics['linear_regression'] = metrics
        
        print(f"✅ Linear Regression trained")
        self._print_metrics(metrics)
        
        return model, metrics
    
    def train_random_forest(self, n_estimators=100, max_depth=15):
        """
        Train Random Forest model
        """
        print("\n" + "="*80)
        print("🌲 TRAINING RANDOM FOREST")
        print("="*80)
        
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=self.random_state,
            n_jobs=-1
        )
        
        model.fit(self.X_train, self.y_train)
        
        # Predictions
        y_pred_train = model.predict(self.X_train)
        y_pred_val = model.predict(self.X_val)
        y_pred_test = model.predict(self.X_test)
        
        # Metrics
        metrics = {
            'train': self._calculate_metrics(self.y_train, y_pred_train),
            'val': self._calculate_metrics(self.y_val, y_pred_val),
            'test': self._calculate_metrics(self.y_test, y_pred_test)
        }
        
        self.models['random_forest'] = model
        self.predictions['random_forest'] = {
            'train': y_pred_train,
            'val': y_pred_val,
            'test': y_pred_test
        }
        self.metrics['random_forest'] = metrics
        
        print(f"✅ Random Forest trained")
        self._print_metrics(metrics)
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': self.features,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n🎯 Top 10 Important Features:")
        for i, row in feature_importance.head(10).iterrows():
            print(f"   {row['feature']:30s} {row['importance']:.4f}")
        
        return model, metrics
    
    def train_xgboost(self, n_estimators=100, max_depth=6, learning_rate=0.1):
        """
        Train XGBoost model
        """
        print("\n" + "="*80)
        print("🚀 TRAINING XGBOOST")
        print("="*80)
        
        model = xgb.XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=self.random_state,
            n_jobs=-1,
            early_stopping_rounds=10
        )
        
        model.fit(
            self.X_train, self.y_train,
            eval_set=[(self.X_val, self.y_val)],
            verbose=False
        )
        
        # Predictions
        y_pred_train = model.predict(self.X_train)
        y_pred_val = model.predict(self.X_val)
        y_pred_test = model.predict(self.X_test)
        
        # Metrics
        metrics = {
            'train': self._calculate_metrics(self.y_train, y_pred_train),
            'val': self._calculate_metrics(self.y_val, y_pred_val),
            'test': self._calculate_metrics(self.y_test, y_pred_test)
        }
        
        self.models['xgboost'] = model
        self.predictions['xgboost'] = {
            'train': y_pred_train,
            'val': y_pred_val,
            'test': y_pred_test
        }
        self.metrics['xgboost'] = metrics
        
        print(f"✅ XGBoost trained")
        self._print_metrics(metrics)
        
        return model, metrics
    
    def train_gradient_boosting(self, n_estimators=200, learning_rate=0.1, max_depth=5):
        """
        Train Gradient Boosting model (sklearn alternative to LSTM for time series)
        """
        print("\n" + "="*80)
        print("🧠 TRAINING GRADIENT BOOSTING")
        print("="*80)
        
        model = GradientBoostingRegressor(
            n_estimators=n_estimators,
            learning_rate=learning_rate,
            max_depth=max_depth,
            random_state=self.random_state
        )
        
        print(f"   • Training with {n_estimators} estimators...")
        model.fit(self.X_train, self.y_train)
        
        # Predictions
        y_pred_train = model.predict(self.X_train)
        y_pred_val = model.predict(self.X_val)
        y_pred_test = model.predict(self.X_test)
        
        # Metrics
        metrics = {
            'train': self._calculate_metrics(self.y_train, y_pred_train),
            'val': self._calculate_metrics(self.y_val, y_pred_val),
            'test': self._calculate_metrics(self.y_test, y_pred_test)
        }
        
        self.models['gradient_boosting'] = model
        self.predictions['gradient_boosting'] = {
            'train': y_pred_train,
            'val': y_pred_val,
            'test': y_pred_test
        }
        self.metrics['gradient_boosting'] = metrics
        
        print(f"✅ Gradient Boosting trained")
        self._print_metrics(metrics)
        
        return model, metrics
    
    def train_ensemble_stacking(self):
        """
        Train ensemble model using stacking
        """
        print("\n" + "="*80)
        print("🎯 TRAINING ENSEMBLE (STACKING)")
        print("="*80)
        
        # Base learners
        base_learners = [
            ('ridge', Ridge(alpha=1.0, random_state=self.random_state)),
            ('rf', RandomForestRegressor(n_estimators=50, max_depth=10, random_state=self.random_state, n_jobs=-1)),
            ('xgb', xgb.XGBRegressor(n_estimators=50, max_depth=4, random_state=self.random_state, n_jobs=-1))
        ]
        
        # Meta learner
        meta_learner = Ridge(alpha=0.5)
        
        # Stacking ensemble
        ensemble = StackingRegressor(
            estimators=base_learners,
            final_estimator=meta_learner,
            cv=5
        )
        
        print(f"   • Base learners: Ridge, Random Forest, XGBoost")
        print(f"   • Meta learner: Ridge Regression")
        print(f"   • Cross-validation: 5 folds")
        
        # Train on scaled data
        ensemble.fit(self.X_train_scaled, self.y_train)
        
        # Predictions
        y_pred_train = ensemble.predict(self.X_train_scaled)
        y_pred_val = ensemble.predict(self.X_val_scaled)
        y_pred_test = ensemble.predict(self.X_test_scaled)
        
        # Metrics
        metrics = {
            'train': self._calculate_metrics(self.y_train, y_pred_train),
            'val': self._calculate_metrics(self.y_val, y_pred_val),
            'test': self._calculate_metrics(self.y_test, y_pred_test)
        }
        
        self.ensemble_model = ensemble
        self.predictions['ensemble'] = {
            'train': y_pred_train,
            'val': y_pred_val,
            'test': y_pred_test
        }
        self.metrics['ensemble'] = metrics
        
        print(f"✅ Ensemble model trained")
        self._print_metrics(metrics)
        
        return ensemble, metrics
    
    def hyperparameter_tuning_random_forest(self, n_iter=20):
        """
        Hyperparameter tuning for Random Forest using RandomizedSearchCV
        """
        print("\n" + "="*80)
        print("🔧 HYPERPARAMETER TUNING - RANDOM FOREST")
        print("="*80)
        
        param_distributions = {
            'n_estimators': randint(50, 200),
            'max_depth': randint(5, 30),
            'min_samples_split': randint(2, 20),
            'min_samples_leaf': randint(1, 10),
            'max_features': ['sqrt', 'log2', None]
        }
        
        rf = RandomForestRegressor(random_state=self.random_state, n_jobs=-1)
        
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=5)
        
        print(f"   • Parameter space: {len(param_distributions)} parameters")
        print(f"   • Iterations: {n_iter}")
        print(f"   • CV strategy: TimeSeriesSplit (5 splits)")
        print(f"   • Searching...")
        
        search = RandomizedSearchCV(
            rf,
            param_distributions=param_distributions,
            n_iter=n_iter,
            cv=tscv,
            scoring='neg_mean_squared_error',
            random_state=self.random_state,
            n_jobs=-1,
            verbose=0
        )
        
        search.fit(self.X_train, self.y_train)
        
        print(f"\n✅ Best parameters found:")
        for param, value in search.best_params_.items():
            print(f"   • {param}: {value}")
        
        self.best_params['random_forest'] = search.best_params_
        
        # Train with best params
        best_model = search.best_estimator_
        y_pred_test = best_model.predict(self.X_test)
        test_rmse = np.sqrt(mean_squared_error(self.y_test, y_pred_test))
        test_r2 = r2_score(self.y_test, y_pred_test)
        
        print(f"\n📊 Test Performance (Tuned RF):")
        print(f"   • RMSE: {test_rmse:.4f}")
        print(f"   • R²:   {test_r2:.4f}")
        
        return search.best_estimator_, search.best_params_
    
    def hyperparameter_tuning_xgboost(self, n_iter=20):
        """
        Hyperparameter tuning for XGBoost using RandomizedSearchCV
        """
        print("\n" + "="*80)
        print("🔧 HYPERPARAMETER TUNING - XGBOOST")
        print("="*80)
        
        param_distributions = {
            'n_estimators': randint(50, 300),
            'max_depth': randint(3, 10),
            'learning_rate': uniform(0.01, 0.3),
            'subsample': uniform(0.6, 0.4),
            'colsample_bytree': uniform(0.6, 0.4),
            'min_child_weight': randint(1, 10)
        }
        
        xgb_model = xgb.XGBRegressor(random_state=self.random_state, n_jobs=-1)
        
        # Time series cross-validation
        tscv = TimeSeriesSplit(n_splits=5)
        
        print(f"   • Parameter space: {len(param_distributions)} parameters")
        print(f"   • Iterations: {n_iter}")
        print(f"   • CV strategy: TimeSeriesSplit (5 splits)")
        print(f"   • Searching...")
        
        search = RandomizedSearchCV(
            xgb_model,
            param_distributions=param_distributions,
            n_iter=n_iter,
            cv=tscv,
            scoring='neg_mean_squared_error',
            random_state=self.random_state,
            n_jobs=-1,
            verbose=0
        )
        
        search.fit(self.X_train, self.y_train)
        
        print(f"\n✅ Best parameters found:")
        for param, value in search.best_params_.items():
            print(f"   • {param}: {value if not isinstance(value, float) else f'{value:.4f}'}")
        
        self.best_params['xgboost'] = search.best_params_
        
        # Train with best params
        best_model = search.best_estimator_
        y_pred_test = best_model.predict(self.X_test)
        test_rmse = np.sqrt(mean_squared_error(self.y_test, y_pred_test))
        test_r2 = r2_score(self.y_test, y_pred_test)
        
        print(f"\n📊 Test Performance (Tuned XGBoost):")
        print(f"   • RMSE: {test_rmse:.4f}")
        print(f"   • R²:   {test_r2:.4f}")
        
        return search.best_estimator_, search.best_params_
    
    def _calculate_metrics(self, y_true, y_pred):
        """
        Calculate regression metrics
        """
        return {
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mae': mean_absolute_error(y_true, y_pred),
            'r2': r2_score(y_true, y_pred)
        }
    
    def _print_metrics(self, metrics):
        """
        Print metrics in a formatted way
        """
        print(f"\n📊 Performance Metrics:")
        print(f"{'Split':<12} {'RMSE':<12} {'MAE':<12} {'R²':<12}")
        print("-" * 48)
        for split in ['train', 'val', 'test']:
            m = metrics[split]
            print(f"{split.capitalize():<12} {m['rmse']:<12.4f} {m['mae']:<12.4f} {m['r2']:<12.4f}")
    
    def compare_models(self):
        """
        Compare all trained models
        """
        print("\n" + "="*80)
        print("📊 MODEL COMPARISON")
        print("="*80)
        
        comparison = []
        for model_name, metrics in self.metrics.items():
            comparison.append({
                'Model': model_name.replace('_', ' ').title(),
                'Train RMSE': metrics['train']['rmse'],
                'Val RMSE': metrics['val']['rmse'],
                'Test RMSE': metrics['test']['rmse'],
                'Test R²': metrics['test']['r2']
            })
        
        df_comparison = pd.DataFrame(comparison).sort_values('Test RMSE')
        
        print(f"\n🏆 Models Ranked by Test RMSE (Lower is better):\n")
        print(df_comparison.to_string(index=False))
        
        # Best model
        best_model = df_comparison.iloc[0]['Model']
        best_rmse = df_comparison.iloc[0]['Test RMSE']
        best_r2 = df_comparison.iloc[0]['Test R²']
        
        print(f"\n🥇 Best Model: {best_model}")
        print(f"   • Test RMSE: {best_rmse:.4f}")
        print(f"   • Test R²: {best_r2:.4f}")
        
        return df_comparison
    
    def save_models(self, output_dir='models'):
        """
        Save all trained models
        """
        print("\n" + "="*80)
        print("💾 SAVING MODELS")
        print("="*80)
        
        Path(output_dir).mkdir(exist_ok=True)
        
        # Save sklearn/xgboost models
        for name, model in self.models.items():
            filepath = f"{output_dir}/{name}_model.pkl"
            with open(filepath, 'wb') as f:
                pickle.dump(model, f)
            print(f"✅ Saved {name} to {filepath}")
        
        # Save ensemble
        if self.ensemble_model:
            filepath = f"{output_dir}/ensemble_model.pkl"
            with open(filepath, 'wb') as f:
                pickle.dump(self.ensemble_model, f)
            print(f"✅ Saved ensemble to {filepath}")
        
        # Save scaler
        filepath = f"{output_dir}/scaler.pkl"
        with open(filepath, 'wb') as f:
            pickle.dump(self.scaler, f)
        print(f"✅ Saved scaler to {filepath}")
        
        # Save metrics
        filepath = f"{output_dir}/metrics.json"
        with open(filepath, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        print(f"✅ Saved metrics to {filepath}")
        
        # Save best parameters
        if self.best_params:
            filepath = f"{output_dir}/best_params.json"
            with open(filepath, 'w') as f:
                json.dump(self.best_params, f, indent=2)
            print(f"✅ Saved best parameters to {filepath}")
        
        print(f"\n✅ All models saved to '{output_dir}/' directory")


# Example usage
if __name__ == "__main__":
    # Initialize pipeline
    pipeline = AQIPredictionPipeline(target='aqi', random_state=42)
    
    # Load data
    pipeline.load_data('processed_air_quality_data.csv')
    
    # Select features
    pipeline.select_features(feature_set='recommended')
    
    # Split data (time-series aware)
    pipeline.time_series_split(train_size=0.7, val_size=0.15, test_size=0.15)
    
    # Train individual models
    pipeline.train_linear_regression()
    pipeline.train_random_forest(n_estimators=100, max_depth=15)
    pipeline.train_xgboost(n_estimators=100, max_depth=6, learning_rate=0.1)
    pipeline.train_gradient_boosting(n_estimators=200, learning_rate=0.1, max_depth=5)
    
    # Train ensemble
    pipeline.train_ensemble_stacking()
    
    # Hyperparameter tuning (optional - takes time)
    # pipeline.hyperparameter_tuning_random_forest(n_iter=20)
    # pipeline.hyperparameter_tuning_xgboost(n_iter=20)
    
    # Compare all models
    pipeline.compare_models()
    
    # Save models
    pipeline.save_models(output_dir='models')
