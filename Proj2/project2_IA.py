import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score

RANDOM_STATE = 1000

def classification():
    X = df_encoded.drop(columns=["Churn"]) # remove "Churn" as a variable to determine the churn
    y = df_encoded["Churn"] # Use the "Churn" column as the target column to train
    
    # Splits dataset by rows into training set (data with which pattern recognition is trained) and test section (data with which knowledge is evaluated)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)
    
    # Derive decisions from noticed relationships in data
    model = RandomForestClassifier(random_state=RANDOM_STATE)
    model.fit(X_train, y_train)
    
    # Feature importance
    importance_df = pd.DataFrame({
        "Feature": X.columns,
        "Importance": model.feature_importances_
    })

    importance_df = importance_df.sort_values(by="Importance", ascending=False)

    print("\nFeature Importance:")
    print(importance_df)
    
    # Prediction of probabilities (between 0 and 1)
    probabilities = model.predict_proba(X_test)[:, 1]
    predictions = model.predict(X_test)
    
    # Risk Categories for readability in the output
    def risk_level(prob):
        if prob < 0.2:
            return "Very Low Risk"
        elif prob < 0.4:
            return "Low Risk"
        elif prob < 0.6:
            return "Medium Risk"
        elif prob < 0.8:
            return "High Risk"
        else:
            return "Very High Risk"
        
    
    risk_categories = [risk_level(p) for p in probabilities]
    
    # Output dataframe
    results = pd.DataFrame({
        "Customer_ID": df.loc[X_test.index, "Customer_ID"],
        "Churn_Prediction": predictions,
        "Churn_Probability": probabilities,
        "Risk_Level": risk_categories,
        "Real_Value": y_test.values
    })
    results["Correct_Prediction"] = results["Real_Value"] == results["Churn_Prediction"]

    accuracy = accuracy_score(y_test, predictions)
    print(f"\nAccuracy do Modelo: {accuracy:.2%}")

    return results

def cluster():
    X = df_encoded.drop(columns=["Churn"]) # remove "Churn" as a variable to determine the churn
    
    # Normalise values to avoid domination by variables with large numerical ranges
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Find natural groups based on customer similarity (clustering number is arbitrary)
    kmeans = KMeans(n_clusters=4, random_state=RANDOM_STATE)
    clusters = kmeans.fit_predict(X_scaled)
    
    # Adds a "Cluster" column to represent in which cluster said member is grouped into
    df["Cluster"] = clusters
    
    return df


def getInput():
    input_folder = "Inputs"

    # Get all files in the folder (checks if the path file contains the folder)
    files = [f for f in os.listdir(input_folder) if os.path.isfile(os.path.join(input_folder, f))]

    # Show menu
    print("\nAvailable input files:")
    for i, file in enumerate(files):
        print(f"{i + 1}. {file}")

    # Choose file (also verifies if input is a number in the correct range)
    while True:
        try:
            choice = int(input("Select a file by number: ")) - 1
            if 0 <= choice < len(files):
                break
            else:
                print("Invalid number, try again.")
        except ValueError:
            print("Please enter a number.")

    # Get full path
    name_input = os.path.join(input_folder, files[choice])

    print(f"\nSelected: {name_input}")

    filename = os.path.basename(name_input) # gets only the name of the file, removing the path
    base, ext = os.path.splitext(filename) # splits file name and extension

    # Read file
    if ext == ".csv":
        df = pd.read_csv(name_input)

    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(name_input)

    else:
        raise ValueError(f"Unsupported file type: {ext}")

    # Remove spaces in case there are any
    df.columns = df.columns.str.strip()

    return base, ext, df


def output(mode, filename, ext, results):
    output_folder = "Outputs"

    if mode == 1:
        operation_output = "_classification"
    elif mode == 2:
        operation_output = "_clustering"

    if ext == ".csv":
        name_output = os.path.join(output_folder, filename + operation_output + ".csv")
        results.to_csv(name_output, index=False)

    elif ext in [".xlsx", ".xls"]:
        name_output = os.path.join(output_folder, filename + operation_output + ".xlsx")
        results.to_excel(name_output, index=False)

    print(f"\nOutput written to: {name_output}")



#---------MENU---------#

filename, ext, df = getInput()

# Choose Machine Learning mode to use on the data set
print("\nOperations:")
print("1. Churn Classification")
print("2. Customer Clustering")

while True:
    try:
        mode = int(input("Choose operation: "))
        if mode in [1, 2]:
            break
        else:
            print("Invalid number, try again.")
    except ValueError:
        print("Please enter a number.")


df_features = df.drop(columns=["Customer_ID"])
df_encoded = pd.get_dummies(df_features, drop_first=True) # Convert categorical variables into numerical dummy variables

# Classification mode
if mode == 1:
    results = classification()
    output(1, filename, ext, results)
    
# Cluster mode
elif mode == 2:
    results = cluster()
    output(2, filename, ext, results)
