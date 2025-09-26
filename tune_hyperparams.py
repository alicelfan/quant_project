import itertools
import numpy as np
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from backtest import scorer


def get_splits(data, num_splits):
    fold_size = len(data) // num_splits
    folds_idx = [
        np.arange(split * fold_size, (split + 1) * fold_size if split != num_splits - 1 else len(data))
        for split in range(num_splits)
    ]
    return folds_idx

def eval_params_on_single_fold(fold, params, interval="day"):
    rsi_buy = params["rsi buy"]
    rsi_sell = params["rsi sell"]
    williamR_buy = params["william R buy"]
    williamR_sell = params["william R sell"]
    realized_pnl, sharpe_ratio = scorer(fold, williamR_buy, williamR_sell, rsi_buy, rsi_sell, interval)
    return realized_pnl, sharpe_ratio

def eval_params_on_multiple_folds(data, fold_indices, params):
    scores = []
    for fold_idx in fold_indices:
        train_fold = data.iloc[fold_idx]
        pnl_train, sharpe_ratio = eval_params_on_single_fold(train_fold, params)
        scores.append((pnl_train, sharpe_ratio))
    return scores

def get_param_combos():
    grid = {"rsi buy" : np.arange(5, 45, 5),
            "rsi sell" : np.arange(95, 55, -5), 
            "william R buy": np.arange(-95, -55, 5), 
            "william R sell" : np.arange(-5, -45, -5)}
    keys, values = zip(*grid.items())
    param_combos = [dict(zip(keys, val)) for val in itertools.product(*values)]
    return param_combos

def annualize_pnl_pct(pnl_pct, period):
    if period == "2y":
        T = 0.5
    #elif period == "2y":
    #    T = 2
    #else:
     #   T = 1
    annualized_PNL_dec = (1 + pnl_pct / 100) ** (1/T) - 1
    return annualized_PNL_dec * 100

def tune_hyperparams(data, test_size=0.25, interval = "day", period="1y"):
    train, test = train_test_split(data, test_size=test_size, shuffle=False)
    param_combos = get_param_combos()
    best_overall_combined_score = -np.inf
    best_params = None
    overall_scores = (0, 0)
    for total_splits in tqdm(range(3, 8), unit = "split"):
        fold_indices = get_splits(train, total_splits)
        best_split_combined_score= -np.inf
        best_split_params = None
        split_scores = (0, 0)
        for param in param_combos:
            scores = eval_params_on_multiple_folds(train, fold_indices, param)
            avg_pnl = sum(score[0] for score in scores) / len(scores)
            avg_PNL_pct = (avg_pnl / 100000) * 100
            annual_pnl_pct = annualize_pnl_pct(avg_PNL_pct, period)
            avg_sharpe_ratio = sum(score[1] for score in scores) / len(scores)
            scores = (annual_pnl_pct, avg_sharpe_ratio)
            combined_score = 0.3 * avg_sharpe_ratio + 0.7 * annual_pnl_pct
            if (combined_score >= best_split_combined_score):
                best_split_params = param
                best_split_combined_score = combined_score
                split_scores = scores

        if best_split_combined_score >= best_overall_combined_score:
            best_split = {"num_splits": total_splits}
            best_params = {**best_split_params, **best_split}
            best_overall_combined_score = best_split_combined_score
            overall_scores = split_scores
    
    print(overall_scores)
    print(best_params)
    final_PNL, final_Sharpe_Ratio = eval_params_on_single_fold(test, best_params, interval)
    final_PNL_pct = (final_PNL / 100000) * 100
    print("final metrics -- test pnl:", final_PNL, "test pnl pct:", final_PNL_pct, "test sharpe ratio:", final_Sharpe_Ratio)
    return final_PNL, final_PNL_pct, final_Sharpe_Ratio