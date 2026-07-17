🏡 House Price Prediction 

📈 Predict house prices using multiple Machine Learning Regression Algorithms and identify the best-performing model.

📖 Project Overview

The House Price Prediction project predicts residential property prices using supervised machine learning techniques. Multiple regression algorithms were trained and compared to determine the most accurate model for estimating house prices.

The project uses the California Housing Dataset from Scikit-learn and evaluates each model using standard regression metrics. After comparing all models, XGBoost Regressor achieved the highest prediction accuracy and was selected as the final model.

✨ Key Features
📂 Data Collection & Processing

📥 Loaded the California Housing Dataset from Scikit-learn.

🧹 Cleaned and preprocessed the dataset using Pandas and NumPy.

🔄 Performed feature engineering and data transformation.

🔀 Split the dataset into training and testing sets for model evaluation.

📊 Data Visualization

The project includes various visualizations to understand the dataset and feature relationships.

📈 Histogram plots
📉 Scatter plots
🔥 Correlation heatmap
📋 Feature distribution analysis
🏠 House price distribution

Visualization libraries used:

🎨 Matplotlib
🌊 Seaborn
🤖 Machine Learning Models

The following machine learning regression algorithms were implemented and compared:

📈 Linear Regression – Used as the baseline regression model.
👥 K-Nearest Neighbors (KNN) Regressor – Predicts house prices based on nearby similar data points.
🌳 Random Forest Regressor – Uses multiple decision trees to improve prediction accuracy.
🚀 Gradient Boosting Regressor – Sequentially improves predictions by correcting previous errors.
⭐ XGBoost Regressor – An optimized gradient boosting algorithm with built-in regularization that achieved the best overall performance.
🏆 Best Performing Model
⭐ XGBoost Regressor

Among all the regression algorithms tested, XGBoost Regressor delivered the highest prediction accuracy.

✅ Why XGBoost?
🚀 Highest prediction accuracy.
📊 Highest R² Score.
📉 Lowest Mean Absolute Error (MAE).
📌 Lowest Mean Squared Error (MSE).
📈 Lowest Root Mean Squared Error (RMSE).
⚡ Fast training and prediction speed.
🌲 Handles complex nonlinear relationships effectively.
🛡️ Reduces overfitting through regularization.
📏 Model Evaluation

The regression models were evaluated using:

📊 R² Score
📉 Mean Absolute Error (MAE)
📈 Mean Squared Error (MSE)
📌 Root Mean Squared Error (RMSE)

The predicted house prices were compared with the actual values using scatter plots to visualize model performance.

🔄 Project Workflow
📂 Load California Housing Dataset
        │
        ▼
🧹 Data Cleaning & Preprocessing
        │
        ▼
📊 Exploratory Data Analysis (EDA)
        │
        ▼
📈 Data Visualization
        │
        ▼
🔀 Train-Test Split
        │
        ▼
🤖 Train Multiple Regression Models
        │
        ├── 📈 Linear Regression
        ├── 👥 KNN Regressor
        ├── 🌳 Random Forest Regressor
        ├── 🚀 Gradient Boosting Regressor
        └── ⭐ XGBoost Regressor
        │
        ▼
📏 Evaluate Model Performance
        │
        ▼
🏆 Select Best Model (XGBoost)
        │
        ▼
🏡 Predict House Prices
        │
        ▼
📉 Visualize Results


🛠️ Technologies Used
🐍 Python
🐼 Pandas
🔢 NumPy
📊 Matplotlib
🎨 Seaborn
🤖 Scikit-learn
⚡ XGBoost
📓 Jupyter Notebook / Google Colab

🚀 Getting Started

📥 Clone the Repository
gh repo clone MYoussef885/House_Price_Prediction

📦 Install Required Libraries
pip install numpy pandas matplotlib seaborn scikit-learn xgboost

▶️ Run the Project
📓 Open the notebook in Jupyter Notebook or Google Colab.
▶️ Execute the notebook cells sequentially.
📊 Compare the performance of all regression models.
🏆 Observe that XGBoost provides the best prediction accuracy.
🎯 Conclusion

This project demonstrates the implementation and comparison of multiple machine learning regression algorithms for house price prediction.

Although Linear Regression, KNN, Random Forest, and Gradient Boosting produced reliable results, XGBoost Regressor achieved the highest predictive performance with the best accuracy and the lowest prediction error.

⭐ Final Selected Model: XGBoost Regressor

📄 License

📜 This project is licensed under the MIT License.
