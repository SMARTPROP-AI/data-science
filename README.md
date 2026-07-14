PROPVALUATE AI
# 🏡 House Price Prediction using Machine Learning

## 📌 Project Overview

This project predicts house prices using Machine Learning by comparing the performance of five different regression algorithms. The objective is to identify the model with the highest prediction accuracy while providing an efficient and scalable solution for real estate price estimation.

The project performs data preprocessing, feature engineering, model training, hyperparameter tuning, model evaluation, and prediction. Among all the models, **XGBoost** achieved the highest prediction accuracy and was selected as the final model.



## 🎯 Objectives

- Predict house prices accurately.
- Compare multiple Machine Learning algorithms.
- Evaluate models using regression metrics.
- Select the best-performing model.
- Save the trained model for deployment.
- Provide a simple and reusable prediction pipeline.



# 📂 Project Structure

```
House-Price-Prediction/
│
├── dataset/
│   ├── housing.csv
│   ├── train.csv
│   └── test.csv
│
├── models/
│   ├── xgboost_model.pkl
│   ├── random_forest.pkl
│   ├── knn.pkl
│   ├── linear_regression.pkl
│   └── gradient_boosting.pkl
│
├── notebooks/
│   └── model_training.ipynb
│
├── src/
│   ├── preprocessing.py
│   ├── train.py
│   ├── evaluate.py
│   └── predict.py
│
├── app.py
├── requirements.txt
├── README.md
└── LICENSE
```



# 🤖 Machine Learning Algorithms Used

## 1️⃣ XGBoost Regressor

- Best overall performance
- Handles missing values
- Prevents overfitting using regularization
- Fast and highly accurate
- Final model selected

**Accuracy (R² Score): 88.9%**

---

## 2️⃣ Random Forest Regressor

- Ensemble learning method
- Multiple Decision Trees
- Reduces variance
- Good generalization

**Accuracy (R² Score): 89.4%**

---

## 3️⃣ Gradient Boosting Regressor

- Sequential boosting algorithm
- Corrects previous model errors
- Good prediction performance

**Accuracy (R² Score): 92.9%**

---

## 4️⃣ Linear Regression

- Baseline regression model
- Simple and interpretable
- Fast training

**Accuracy (R² Score): 91.5%**

---

## 5️⃣ K-Nearest Neighbors (KNN)

- Instance-based learning
- Predicts using nearest neighbors
- Sensitive to feature scaling

**Accuracy (R² Score): 77.6%**



# 🔍 Evaluation Metrics

The models were evaluated using:

- R² Score
- Mean Absolute Error (MAE)
- Mean Squared Error (MSE)
- Root Mean Squared Error (RMSE)



# ⚙️ Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- XGBoost
- Joblib
- Matplotlib
- Streamlit (Optional)
- Jupyter Notebook



# 📦 Installation

Clone the repository

```bash
git clone https://github.com/yourusername/House-Price-Prediction.git
```

Move into the project

```bash
cd House-Price-Prediction
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the project

```bash
python app.py
```

or

```bash
streamlit run app.py
```



# 📈 Workflow

1. Load Dataset
2. Data Cleaning
3. Handle Missing Values
4. Feature Encoding
5. Feature Scaling
6. Train-Test Split
7. Train Five Models
8. Hyperparameter Tuning
9. Compare Model Performance
10. Save Best Model (XGBoost)
11. Predict House Prices



# 🚀 Features

- Data Preprocessing
- Feature Engineering
- Five Machine Learning Algorithms
- Model Comparison
- Automatic Best Model Selection
- House Price Prediction
- Model Saving
- Easy Deployment



# 🏆 Best Model

After evaluating all algorithms, **XGBoost Regressor** achieved the highest prediction accuracy.

### Why XGBoost?

- Highest Accuracy
- Fast Prediction
- Better Generalization
- Handles Missing Values
- Regularization Prevents Overfitting
- Suitable for Large Datasets

Final Selected Model:

```
XGBoost Regressor
Accuracy: 88.7%
```

---

