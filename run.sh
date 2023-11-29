# reset
# rm -rf ./cache_data/step2_res/*
# rm -rf ./cache_data/step3_res/*


# demo pipeline
# python 0_pipeline.py

# start
python 1_extract_terms.py

echo "Running step 2..."
python 2_extract_more_terms.py

echo "Running step 3..."
python 3_extract_entities.py

echo "Running step 4..."
python 4_extract_relations.py

echo "Running step 5..."
python 5_align_entities.py

echo "Running step 6..."
python 6_construct_KG.py
