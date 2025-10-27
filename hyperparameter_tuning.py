"""
Advanced Hyperparameter Tuning with Rolling Cross-Validation
Demonstrates Grid Search and Bayesian Optimization
"""

from ml_pipeline import AQIPredictionPipeline
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV, RandomizedSearchCV
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
from scipy.stats import uniform, randint
import pandas as pd
import numpy as np


def tune_with_grid_search(pipeline):
    """
    Hyperparameter tuning using GridSearchCV with TimeSeriesSplit
    """
    print("\n" + "="*80)
    print("🔍 GRID SEARCH - RANDOM FOREST")
    print("="*80)
    
    # Define parameter grid
    param_grid = {
        'n_estimators': [50, 100, 150],
        'max_depth': [10, 15, 20],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    
    # Random Forest model
    rf = RandomForestRegressor(random_state=42, n_jobs=-1)
    
    # Time Series Cross-Validation
    tscv = TimeSeriesSplit(n_splits=5)
    
    print(f"   • Parameter grid combinations: {np.prod([len(v) for v in param_grid.values()])}")
    print(f"   • CV splits: 5 (TimeSeriesSplit)")
    print(f"   • Scoring: Negative MSE")
    print(f"   • Searching...")
    
    # Grid Search
    grid_search = GridSearchCV(
        estimator=rf,
        param_grid=param_grid,
        cv=tscv,
        scoring='neg_mean_squared_error',
        n_jobs=-1,
        verbose=1
    )
    
    grid_search.fit(pipeline.X_train, pipeline.y_train)
    
    print(f"\n✅ Grid Search Complete!")
    print(f"\n🏆 Best Parameters:")
    for param, value in grid_search.best_params_.items():
        print(f"   • {param}: {value}")
    
    print(f"\n📊 Best CV Score (Negative MSE): {grid_search.best_score_:.4f}")
    
    # Test performance
    best_model = grid_search.best_estimator_
    from sklearn.metrics import mean_squared_error, r2_score
    
    y_pred_test = best_model.predict(pipeline.X_test)
    test_rmse = np.sqrt(mean_squared_error(pipeline.y_test, y_pred_test))
    test_r2 = r2_score(pipeline.y_test, y_pred_test)
    
    print(f"\n📊 Test Performance:")
    print(f"   • RMSE: {test_rmse:.4f}")
    print(f"   • R²: {test_r2:.4f}")
    
    return grid_search.best_estimator_, grid_search.best_params_


def tune_with_randomized_search(pipeline, n_iter=50):
    """
    Hyperparameter tuning using RandomizedSearchCV (Bayesian-like)
    """
    print("\n" + "="*80)
    print("🎲 RANDOMIZED SEARCH - XGBOOST")
    print("="*80)
    
    # Define parameter distributions
    param_distributions = {
        'n_estimators': randint(50, 300),
        'max_depth': randint(3, 15),
        'learning_rate': uniform(0.01, 0.3),
        'subsample': uniform(0.5, 0.5),
        'colsample_bytree': uniform(0.5, 0.5),
        'min_child_weight': randint(1, 10),
        'gamma': uniform(0, 0.5)
    }
    
    # XGBoost model
    xgb_model = xgb.XGBRegressor(random_state=42, n_jobs=-1)
    
    # Time Series Cross-Validation
    tscv = TimeSeriesSplit(n_splits=5)
    
    print(f"   • Random iterations: {n_iter}")
    print(f"   • CV splits: 5 (TimeSeriesSplit)")
    print(f"   • Scoring: Negative MSE")
    print(f"   • Searching...")
    
    # Randomized Search
    random_search = RandomizedSearchCV(
        estimator=xgb_model,
        param_distributions=param_distributions,
        n_iter=n_iter,
        cv=tscv,
        scoring='neg_mean_squared_error',
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    random_search.fit(pipeline.X_train, pipeline.y_train)
    
    print(f"\n✅ Randomized Search Complete!")
    print(f"\n🏆 Best Parameters:")
    for param, value in random_search.best_params_.items():
        if isinstance(value, float):
            print(f"   • {param}: {value:.4f}")
        else:
            print(f"   • {param}: {value}")
    
    print(f"\n📊 Best CV Score (Negative MSE): {random_search.best_score_:.4f}")
    
    # Test performance
    best_model = random_search.best_estimator_
    from sklearn.metrics import mean_squared_error, r2_score
    
    y_pred_test = best_model.predict(pipeline.X_test)
    test_rmse = np.sqrt(mean_squared_error(pipeline.y_test, y_pred_test))
    test_r2 = r2_score(pipeline.y_test, y_pred_test)
    
    print(f"\n📊 Test Performance:")
    print(f"   • RMSE: {test_rmse:.4f}")
    print(f"   • R²: {test_r2:.4f}")
    
    return random_search.best_estimator_, random_search.best_params_


def rolling_cross_validation_demo(pipeline, n_splits=5):
    """
    Demonstrate rolling/expanding window cross-validation for time series
    """
    print("\n" + "="*80)
    print("📊 ROLLING CROSS-VALIDATION DEMONSTRATION")
    print("="*80)
    
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    from sklearn.ensemble import RandomForestRegressor
    
    tscv = TimeSeriesSplit(n_splits=n_splits)
    
    print(f"   • CV Strategy: TimeSeriesSplit")
    print(f"   • Number of splits: {n_splits}")
    print(f"   • Model: Random Forest")
    
    results = []
    
    print(f"\n🔄 Performing rolling cross-validation...")
    
    for fold, (train_idx, val_idx) in enumerate(tscv.split(pipeline.X_train), 1):
        # Split data
        X_train_fold = pipeline.X_train.iloc[train_idx]
        y_train_fold = pipeline.y_train.iloc[train_idx]
        X_val_fold = pipeline.X_train.iloc[val_idx]
        y_val_fold = pipeline.y_train.iloc[val_idx]
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
        model.fit(X_train_fold, y_train_fold)
        
        # Predict
        y_pred = model.predict(X_val_fold)
        
        # Metrics
        rmse = np.sqrt(mean_squared_error(y_val_fold, y_pred))
        mae = mean_absolute_error(y_val_fold, y_pred)
        r2 = r2_score(y_val_fold, y_pred)
        
        results.append({
            'Fold': fold,
            'Train Size': len(train_idx),
            'Val Size': len(val_idx),
            'RMSE': rmse,
            'MAE': mae,
            'R²': r2
        })
        
        print(f"   Fold {fold}: Train={len(train_idx):3d}, Val={len(val_idx):2d}, RMSE={rmse:6.2f}, R²={r2:.4f}")
    
    # Summary
    results_df = pd.DataFrame(results)
    
    print(f"\n📊 Cross-Validation Summary:")
    print(f"   • Mean RMSE: {results_df['RMSE'].mean():.4f} ± {results_df['RMSE'].std():.4f}")
    print(f"   • Mean MAE:  {results_df['MAE'].mean():.4f} ± {results_df['MAE'].std():.4f}")
    print(f"   • Mean R²:   {results_df['R²'].mean():.4f} ± {results_df['R²'].std():.4f}")
    
    print(f"\n📋 Detailed Results:")
    print(results_df.to_string(index=False))
    
    return results_df


def main():
    print("\n" + "🎯"*40)
    print("ADVANCED HYPERPARAMETER TUNING DEMONSTRATION")
    print("🎯"*40 + "\n")
    
    # Initialize pipeline
    pipeline = AQIPredictionPipeline(target='aqi', random_state=42)
    
    # Load data
    pipeline.load_data('processed_air_quality_data.csv')
    
    # Select features
    pipeline.select_features(feature_set='recommended')
    
    # Split data
    pipeline.time_series_split(train_size=0.7, val_size=0.15, test_size=0.15)
    
    # 1. Rolling Cross-Validation Demo
    rolling_cross_validation_demo(pipeline, n_splits=5)
    
    # 2. Grid Search
    print("\n" + "="*80)
    choice = input("Perform Grid Search? (Takes ~5 minutes) (y/n): ").lower()
    if choice == 'y':
        best_rf, best_params_rf = tune_with_grid_search(pipeline)
    
    # 3. Randomized Search
    print("\n" + "="*80)
    choice = input("Perform Randomized Search? (Takes ~3 minutes) (y/n): ").lower()
    if choice == 'y':
        best_xgb, best_params_xgb = tune_with_randomized_search(pipeline, n_iter=50)
    
    print("\n" + "="*80)
    print("✅ HYPERPARAMETER TUNING COMPLETE!")
    print("="*80)
    
    print(f"\n✨ Demonstrated:")
    print(f"   ✅ Rolling/Expanding window cross-validation (TimeSeriesSplit)")
    print(f"   ✅ Grid Search with exhaustive parameter search")
    print(f"   ✅ Randomized Search (Bayesian-like optimization)")
    print(f"   ✅ Time-series aware validation")
    
    print(f"\n🎯 These techniques prevent data leakage in time series!")
    print(f"   • No future data used to predict past")
    print(f"   • Respects temporal order")
    print(f"   • Production-ready validation strategy")
    
    print("\n✨ Tuning demonstration complete! ✨\n")


if __name__ == "__main__":
    main()
