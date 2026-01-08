Projet : Backtesting Python – Module Quant A
1. Description générale

Ce projet s’inscrit dans le cadre de l’UV Python / Git / Linux.
L’objectif général est de construire une application de backtesting permettant d’analyser la performance d’un actif financier à travers différentes stratégies d’investissement.

L’application utilise Streamlit pour proposer une interface simple et interactive.
Le module Quant A se concentre sur l’analyse d’un seul actif à la fois et propose :

Chargement des données financières via yfinance

Deux stratégies de backtesting

Calcul de métriques de performance

Affichage interactif des résultats

2. Fonctionnalités principales du module Quant A
2.1. Analyse d’un actif unique

L’utilisateur choisit un ticker (exemple : BTC-USD, ENGI.PA, EURUSD=X).
Les données sont téléchargées via l’API Yahoo Finance.

2.2. Stratégies implémentées

Deux stratégies sont disponibles :

Buy & Hold
Investissement unique au début → conservation jusqu’à la fin.

MA Crossover (Momentum)

Calcul de deux moyennes mobiles : courte et longue

Position investie si MA courte > MA longue

Position en cash sinon

Stratégie typique de suivi de tendance

Ces stratégies sont codées dans le fichier :
quant_a/strategies_single_asset.py

2.3. Métriques de performance

Calculées dans quant_a/metrics_single_asset.py :

Sharpe ratio

Max drawdown

Performance totale

Rendements quotidiens

Ces indicateurs permettent d’évaluer la performance et le risque.

2.4. Interface Streamlit

L’interface permet à l’utilisateur :

De choisir la période d’analyse

De sélectionner la périodicité (1d, 1h, etc.)

De choisir la stratégie

D’ajuster les paramètres (moyennes mobiles, capital initial)

De lancer le backtest via un bouton

D’afficher le graphique principal :
prix de l’actif + valeur cumulée de la stratégie

De consulter les données récentes dans un tableau

L'interface est définie dans :
quant_a/page_quant_a.py

3. Architecture du projet
PROJET-PYTHON-GIT-LINUX/
│
├── app.py                      # Lancement principal de l'application Streamlit
├── requirements.txt            # Dépendances Python
├── .streamlit/
│     └── config.toml           # Thème et configuration Streamlit
│
└── quant_a/
      ├── data_single_asset.py        # Chargement des données via yfinance
      ├── strategies_single_asset.py  # Stratégies de backtesting
      ├── metrics_single_asset.py     # Calcul des métriques
      ├── page_quant_a.py             # Interface dédiée Quant A
      └── __init__.py


Cette structure suit les bonnes pratiques : modularité, lisibilité du code, séparation des responsabilités.

4. Installation et exécution
4.1. Cloner le projet
git clone https://github.com/benjatt974/PROJET-PYTHON-GIT-LINUX.git
cd PROJET-PYTHON-GIT-LINUX

4.2. Créer et activer un environnement virtuel
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows PowerShell

4.3. Installer les dépendances
pip install -r requirements.txt

4.4. Lancer l'application
streamlit run app.py


L’application sera disponible dans le navigateur à l’adresse :
http://localhost:8501

5. Validation par scénarios (tests cohérents)

Deux tests majeurs ont été réalisés pour valider le fonctionnement :

5.1. Marché haussier (2020-2021)

Résultat attendu :

Buy & Hold très performant

MA Crossover légèrement en retard mais cohérent

Sharpe ratio élevé

Drawdown modéré

5.2. Marché baissier (2021-2022)

Résultat attendu :

Buy & Hold fortement négatif (≥ -70%)

MA Crossover limite fortement les pertes

Max drawdown très réduit

Sharpe moins négatif

Les résultats obtenus confirment la cohérence complète du module.

6. Améliorations possibles (optionnelles)

Ajouter une stratégie supplémentaire (RSI, breakout, Bollinger Bands)

Ajouter un modèle simple de prévision (régression linéaire, ARIMA)

Ajouter un second graphique (signal buy/sell)

Intégration avec le module Quant B (multi-actifs)

7. Auteurs

Projet réalisé dans le cadre de l’UV Python / Git / Linux (ESILV).
Module Quant A développé par : benjatt974

Project: Python Backtesting – Quant B Module

1. General description
. This project is part of the Python / Git / Linux course.
. The Quant B module focuses on multi-asset portfolio backtesting and analysis.
. The application is built with Streamlit to provide an interactive dashboard.
. Main features include:
. Multi-asset data loading via yfinance
. Portfolio allocation (weighting methods)
. Portfolio backtest (Buy & Hold)
. Optional MA Cross strategy applied to the portfolio value
. Risk/return metrics and visualizations (base-100, drawdown, correlations)

2. Main features of Quant B

2.1. Multi-asset portfolio analysis
. The user selects at least 3 tickers (example: AAPL, MSFT, GOOGL, BTC-USD, GLD, TLT).
. Price data is downloaded from Yahoo Finance and aligned on a common date index.
. Data loading file:
. quant_b/data_multi_asset.py

2.2. Portfolio allocation / weighting
. Multiple allocation methods are available:
. Equal Weights
. Same weight for each selected asset (1/N)
. Minimum Variance
. Computes weights that minimize portfolio variance
. Optional long-only constraint (no negative weights)
. Max Sharpe Ratio
. Computes weights that maximize a Sharpe-like objective
. Optional long-only constraint (no negative weights)
. Custom Weights
. The user manually sets weights (then weights are normalized)
. Allocation logic is implemented in:
. quant_b/portfolio.py

2.3. Implemented strategies
. Two backtesting approaches are available:
. Portfolio Buy & Hold
. Allocate initial capital using selected weights, then hold until the end
. MA Crossover on portfolio (optional)
. Momentum strategy applied to the portfolio value
. Compute short and long moving averages
. Invested when short MA > long MA
. Otherwise, move to cash (0 exposure)
. Implemented in:
. quant_b/portfolio.py (backtest_ma_cross)

2.4. Performance metrics
. Quant B computes:
. Total Return
. Sharpe Ratio
. Max Drawdown
. Annualized Volatility
. Diversification Ratio
. Correlation matrix (based on daily returns)
. Implemented in:
. quant_b/portfolio.py

2.5. Streamlit interface
. The interface allows the user to:
. Select multiple tickers (multi-select)
. Set start/end dates
. Set initial capital
. Choose an allocation method (Equal / MinVar / MaxSharpe / Custom)
. Enable/disable MA Cross on portfolio
. Tune MA parameters (short/long)
. Run the backtest with a button
. Display results:
. Base-100 performance comparison (assets + portfolio + strategy)
. Weights table
. Correlation matrix
. Drawdown curve
. Metric cards (Return, Volatility, Sharpe, Diversification)
. UI file:
. quant_b/page_quant_b.py

3. Project architecture
. PROJET-PYTHON-GIT-LINUX/
. app.py (Main Streamlit entry point)
. requirements.txt (Python dependencies)
. .streamlit/config.toml (Streamlit theme/config)
. quant_b/
. data_multi_asset.py (Multi-asset data download)
. portfolio.py (Allocation, strategy, metrics)
. page_quant_b.py (Quant B Streamlit UI)
. __init__.py

4. Installation and execution

git clone https://github.com/benjatt974/PROJET-PYTHON-GIT-LINUX.git
cd PROJET-PYTHON-GIT-LINUX

4.2. Create and activate a virtual environment

python -m venv .venv
.venv\Scripts\Activate.ps1

4.3. Install dependencies

pip install -r requirements.txt

4.4. Run the Streamlit app

streamlit run app.py
. The app runs at:
. http://localhost:8501

5. Scenario-based validation (coherent tests)

5.1. Bull market / trending period
. Example: 2020 -> 2021 (QQQ/AAPL/MSFT/GLD)
. Buy & Hold should perform strongly
. Max Sharpe often performs well but may concentrate weights
. Diversification reduces volatility and stabilizes drawdowns
. Sharpe should be relatively high

5.2. Bear market / stress period
. Example: 2021 -> 2022 (risk assets + bonds)
. Buy & Hold can suffer large drawdowns
. MA Cross reduces exposure and limits losses
. Correlation matrix and diversification ratio become very useful

6. Possible improvements (optional)
. Add more allocation methods (Risk Parity, Equal Risk Contribution)
. Add transaction costs / slippage
. Add periodic rebalancing (weekly / monthly)
. Add a signal chart (invested vs cash) for MA Cross
. Add benchmark comparison (e.g., SPY)

7. Authors
. Project developed for the Python / Git / Linux course (ESILV)
. Quant B module developed by: nathanaelbcoquet
