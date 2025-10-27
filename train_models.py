"""
Run Complete ML Pipeline for AQI Prediction
Includes all requested features: Train/Val/Test split, Multiple models, Ensemble, Hyperparameter tuning
"""

from ml_pipeline import AQIPredictionPipeline
import sys


def main():
    print("\n" + "🚀"*40)
    print("AQI PREDICTION - COMPLETE ML PIPELINE")
    print("🚀"*40 + "\n")
    
    # Initialize pipeline
    print("🔧 Initializing ML Pipeline...")
    pipeline = AQIPredictionPipeline(target='aqi', random_state=42)
    
    # Load preprocessed data
    try:
        pipeline.load_data('processed_air_quality_data.csv')
    except FileNotFoundError:
        print("❌ Error: processed_air_quality_data.csv not found!")
        print("Please run: python demo_preprocessing.py first")
        sys.exit(1)
    
    # Feature selection
    pipeline.select_features(feature_set='recommended')
    
    # Time-series aware split
    pipeline.time_series_split(train_size=0.7, val_size=0.15, test_size=0.15)
    
    # Train individual models
    print("\n" + "🎯"*40)
    print("TRAINING INDIVIDUAL MODELS")
    print("🎯"*40)
    
    pipeline.train_linear_regression()
    pipeline.train_random_forest(n_estimators=100, max_depth=15)
    pipeline.train_xgboost(n_estimators=100, max_depth=6, learning_rate=0.1)
    pipeline.train_gradient_boosting(n_estimators=200, learning_rate=0.1, max_depth=5)
    
    # Train ensemble
    print("\n" + "🏆"*40)
    print("TRAINING ENSEMBLE MODEL")
    print("🏆"*40)
    
    pipeline.train_ensemble_stacking()
    
    # Compare models
    comparison = pipeline.compare_models()
    
    # Hyperparameter tuning (optional - comment out if too slow)
    print("\n" + "⚙️"*40)
    print("HYPERPARAMETER TUNING (This may take a few minutes...)")
    print("⚙️"*40)
    
    tune_models = input("\nPerform hyperparameter tuning? (y/n): ").lower()
    
    if tune_models == 'y':
        pipeline.hyperparameter_tuning_random_forest(n_iter=20)
        pipeline.hyperparameter_tuning_xgboost(n_iter=20)
    else:
        print("⏭️ Skipping hyperparameter tuning")
    
    # Save everything
    pipeline.save_models(output_dir='models')
    
    # Final summary
    print("\n" + "="*80)
    print("✅ PIPELINE COMPLETE!")
    print("="*80)
    
    print(f"\n📊 Summary:")
    print(f"   • Models trained: {len(pipeline.models)} individual + 1 ensemble")
    print(f"   • Best model: {comparison.iloc[0]['Model']}")
    print(f"   • Best Test RMSE: {comparison.iloc[0]['Test RMSE']:.4f}")
    print(f"   • Best Test R²: {comparison.iloc[0]['Test R²']:.4f}")
    
    print(f"\n💾 Saved to 'models/' directory:")
    print(f"   • linear_regression_model.pkl")
    print(f"   • random_forest_model.pkl")
    print(f"   • xgboost_model.pkl")
    print(f"   • gradient_boosting_model.pkl")
    print(f"   • ensemble_model.pkl")
    print(f"   • scaler.pkl")
    print(f"   • metrics.json")
    
    print(f"\n🎯 Next Steps:")
    print(f"   1. Review model comparison above")
    print(f"   2. Use best model for predictions")
    print(f"   3. Deploy to production (Flask API)")
    
    print("\n✨ Your AQI prediction models are ready! ✨\n")


if __name__ == "__main__":
    main()
