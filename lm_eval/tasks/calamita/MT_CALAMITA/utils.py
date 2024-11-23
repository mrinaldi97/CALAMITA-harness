import datasets

from typing import List
from evaluate import load



def preprocess_dataset(dataset: datasets.Dataset) -> datasets.Dataset:
    # dataset = dataset.select([i for i in range(4)])      # selecting 4 rows for DEBUG
    return dataset


# post-processing the results
def _search_delimiters(model_output: str) -> str:
    left_delimiter = '<'
    right_delimiter = '>'
    start: int = 0
    end: int = len(model_output)
    if left_delimiter in model_output:
        start = model_output.find(left_delimiter)
    if right_delimiter in model_output:
        end = model_output.find(right_delimiter)

    if len(model_output) < 1:
        return "---"  # empty string as a replacement
    return model_output[start:end].replace('<', '').replace('>', '').strip()

def _check_error_input(ref, pred):
    """
    Returns True if the input is not valid (empty or None)
    """
    if pred:
        if len(pred) < 1:
            print(f"{pred = }")
            return True
    else:
        print(f"{pred = }")
        return True
    if ref:
        if len(ref) < 1:
            print(f"{ref = }")
            return True
    else:
        print(f"{ref = }")
        return True
    
    return False

def single_bleu(ref: str, pred: str) -> float:
    if _check_error_input(ref, pred):
        return 0    # interrupt and return lowest score
    bleu_metric = load("bleu")
    bleu_score = bleu_metric.compute(predictions=[pred], references=[[ref]])
    return bleu_score["bleu"]

def sigle_chrf(ref: str, pred: str) -> float:
    if _check_error_input(ref, pred):
        return 0    # interrupt and return lowest score
    chrf_metric = load("chrf")
    chrf_score = chrf_metric.compute(predictions=[pred], references=[[ref]])
    return chrf_score["score"]

def single_bleurt(ref: str, pred: str) -> float:
    if _check_error_input(ref, pred):
        return 0    # interrupt and return lowest score
    bleurt = load("bleurt", module_type="metric", checkpoint="BLEURT-20")
    result = bleurt.compute(predictions=[pred], references=[ref])
    return result["scores"][0]

def single_comet(source: str, ref: str, pred: str) -> float:
    if _check_error_input(ref, pred):
        return 0    # interrupt and return lowest score
    comet_metric = load("comet")
    comet_score = comet_metric.compute(predictions=[pred], references=[ref], sources=[source])
    return comet_score["scores"][0]

def _get_metrics(
    model_input: str,
    reference_out: str,
    completition: str
    ) -> dict[str, float]:
    """
    Compute the metrics for the MT_CALAMITA task
    """

    # clean completion
    completition = _search_delimiters(completition)

    # BLEU
    bleu_score = single_bleu(ref=reference_out, pred=completition)
    # CHRF
    chrf_score = sigle_chrf(ref=reference_out, pred=completition)
    # BLEURT
    bleurt_score = single_bleurt(ref=reference_out, pred=completition)
    # COMET
    comet_score = single_comet(source=model_input, ref=reference_out, pred=completition)

    return {
        "bleu_score": bleu_score,
        "chrf_score": chrf_score,
        "bleurt_score": bleurt_score,
        "comet_score": comet_score,
    }


def process_results_it_en(doc, results):
    """
    Process the results of the model and return the metrics. Implementation for the **italian to english** task
    Args:
        - doc: the document containing the input and output (keys are the variables from the prompt_template)
        - results: the output of the model (still dunnow why its a list but it doesn't depend on the batchsize)
    Returns:
        - a dictionary containing the metrics (metric_name: metric_value)
    """

    completion = results[0]
    model_input, reference_out = doc["italian"], doc["english"]

    return _get_metrics(
        model_input=model_input, 
        reference_out=reference_out, 
        completition=completion,
    )

def process_results_en_it(doc, results):
    """
    Process the results of the model and return the metrics. Implementation for the **english to italian** task
    Args:
        - doc: the document containing the input and output (keys are the variables from the prompt_template)
        - results: the output of the model (still dunnow why its a list but it doesn't depend on the batchsize)
    Returns:
        - a dictionary containing the metrics (metric_name: metric_value)
    """

    completion = results[0]
    model_input, reference_out = doc["english"], doc["italian"]

    return _get_metrics(
        model_input=model_input, 
        reference_out=reference_out, 
        completition=completion,
    )




