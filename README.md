# AutoRD

* AutoRD: An Automatic and End-to-end Rare Disease Knowledge Graph Construction Framework Based on Ontologies-enhanced Large Language Models


## Quick Start

* 0. put your OPENAI_API_KEY at `env.py`
* 0. get the latest ontolgies on the Internet. [HOOM_en_2.0.owl](https://www.orphadata.com/hoom/), [ORDO_en_4.3.owl](https://www.orphadata.com/ordo/), [mondo.obo](https://mondo.monarchinitiative.org/)
* 0. get the test dataset RareDis-v1 from the authors of [the original paper](https://arxiv.org/abs/2108.01204)



```shell
# data preprocessing
cd data_preprocessing

# put original dataset RareDis at `data_preprocessing/data` and rename it and cover it at `data_preprocessing/data/RareDis-fixed`

# fix some data annotation errors
cd RareDis-fixed
python fix_data.py

cd ../
python generate_data.py
python parse_HOOM.py
python parse_mondo_obo.py
python parse_ORDO.py


# put new generated dataset and processed ontologies at `./data`

# run main code
cd ../
bash run.sh
```

* Find your results at `./cache_data`

## Baselins

```shell
## run baselines
# fine-tuning baseline
cd finetuning_baseline
python main.py

# pure LLM baseline
cd LLM_baseline
python main.py
```