Previsão de churn (clientes que vão sair) para ginásios

## Features and explanations

Churn — the fact of churn for the month in question. (Used as the target column, which will train the AI)
→ Given in different levels of probability (Output only) → 0-20% = Very Low Risk, 20-40% = Low Risk, 40-60% = Medium Risk, 60-80%= High Risk, 80-100% = Very High Risk

Customer_ID → NOT USED FOR THE CHURN

gender — 0 for female, and 1 for male ← ATTENTION: demographic features can introduce bias - behavioural features are normally stronger and more ethical predictors (Maybe remover, mas honestamente acredito que possamos deixar porque é algo interessante de ver no peso determinado da sua importância, mas temos de chamar à atenção)

Near_Location — whether the user lives or works close to the gym’s location (levels of distance like: 0-2km = close, 2-5km = medium, 5-8k = a bit far, 8-10km = far, 10km+ = very far)

Partner — whether the user is an employee of a partner company (the gym has partner companies whose employees get discounts; in those cases the gym stores information on customers' employers)

Promo_friends — whether the user originally signed up through a "bring a friend" offer (they used a friend's promo code when paying for their first membership)

Membership_type - what type of membership does the customer have (basic, standard, premium)

Age - range of ages

Lifetime — the time (in months) since the customer first came to the gym

Fitness goal - Motivation for going to the gym (weight loss, bodybuilding, health, or rehabilitation)

Contract_period — 1 month, 3 months, 6 months, or 1 year

Month_to_end_contract — the months remaining until the contract expires

Workout_with_friends  — whether the user trains alone or with friends

Avg_class_frequency_total — average frequency of classes taken per month over customer's lifetime

Class_frequency_last_month — number of classes taken the previous month

Personal_trainer_contract - if the user as a personal trainer or not

Avg_additional_charges_total — the total amount of money spent on other gym services: cafe, athletic goods, cosmetics, massages, etc.

Avg_visits_total  -  average frequency of gym visits per month over customer’s lifetime

Avg_visits_last_month  - number of gym visits the previous month

Attendance_trend - % change of the customer’s gym attendance over last 5 months

Days_since_last_visit  - number of days since last visit (check for recent inactivity)

Satisfaction_score - customer’s satisfaction over gym’s infrastructure, equipment, and overall experience

Avg_workout_time - how much time the user spends in the gym

Prefered_workout_time - average time of day customer goes to the gym (morning, afternoon-earlier, afternoon-later, night → check if is affected by peak hours)


## How randomness is used

Random_state: it’s used for the test conditions that use randomness to be always the same by fixing a seed → in our case, the seed used is 1000


## Datasets explanation

- gym_churn_(original).csv: original dataset from Kaggle (only with the original features) with added Customer_ID column

- gym_churn_enriched_(new).csv: original dataset enriched with all features mentioned above, but is very linearly/structurally separable in feature space, leading to too much predictability

- gym_churn_extended_20000.csv: extended version of the previous dataset, going from 4000 gym members to 20000, but shows all of the same predictability

- gym_data_enriched_fixed.csv: first attempt at realistic dataset created from scratch derived from the original dataset but with all the features (results ended up very artificial and mostly unrealistic)

- gym_churn_noisy_20000.csv: based on the previous 20000 members dataset but with added noise for realism. Noise was added with the help of Gemini in the following way:

# Asked in prompt:

- contradictory customers (like high satisfaction but churn, low satisfaction but stay, high engagement but churn (life change, relocation), low engagement but stay (contract lock-in))

- softer probabilistic rules

- overlap between classes

- correlated randomness (like small randomness in satisfaction, small randomness in attendance, correlated drift over time)

- inject "real-world failure cases" (like people who renew contracts despite dissatisfaction, people who churn immediately after signing up, seasonal churn spikes, random external churn causes (moving, injury, financial issues))

# Resulting dataset with:
# Contradictory Customer Profiles:

1. High-Satisfaction Churners: Applied to 5% of users with a satisfaction score > 4.5. These represent people who like the gym but might be moving or changing lifestyles.

2. Low-Satisfaction Stayers: Applied to 20% of users with scores < 1.5. These represent "hostage" customers who might stay due to lack of other options or proximity despite being unhappy.

3. High-Engagement Churners: Users with > 5 visits per month who still churn (e.g., sudden relocation).

4. Low-Engagement Stayers: Users with very low attendance but long-term contracts (6–12 months) who are "locked in" and haven't officially churned yet.

# Real-World Failure Cases:Immediate Churn: 

1. Injected "unlucky" signups where users churn within their first month (Lifetime <= 1) regardless of their satisfaction or initial engagement.

Random External Churn: A random 2% baseline churn rate was applied to simulate unpredictable life events like injuries, financial shifts, or job changes that no feature can predict.

# Feature Overlap & Correlated Randomness:

Gaussian Jitter: Added random noise (relative to standard deviation) to Satisfaction_score, Avg_visits_total, Avg_visits_last_month, and Avg_additional_charges_total.This ensures that the boundary between classes is "fuzzy" rather than a hard threshold.

# Global Probabilistic Noise:

A final 3% random label flip was applied across the entire dataset to ensure that no model can reach 100% accuracy, as there is now a fundamental "irreducible error" (Bayes error) present in the data.