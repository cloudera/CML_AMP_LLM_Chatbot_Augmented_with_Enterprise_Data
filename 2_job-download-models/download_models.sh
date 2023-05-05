# This script is used to pre=download files stored with git-lfs in CML Runtimes which do not have git-lfs support
# You can use any models that can be loaded with the huggingface transformers library. See utils/model_embedding_utls.py or utils/moderl_llm_utils.py
EMBEDDING_MODEL_REPO="https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2"
EMBDEDDING_MODEL_COMMIT="7dbbc90392e2f80f3d3c277d6e90027e55de9125"

LLM_MODEL_REPO="https://huggingface.co/h2oai/h2ogpt-oig-oasst1-512-6.9b"
LLM_MODEL_COMMIT="4e336d947ee37d99f2af735d11c4a863c74f8541"


download_lfs_files () {
    echo "These files must be downloaded manually since there is no git-lfs here:"
    git ls-files | git check-attr --stdin filter | awk -F': ' '$3 ~ /lfs/ { print $1}' | while read line; do 
        echo $(git remote get-url $(git remote))/resolve/$(git rev-parse HEAD)/${line}
        curl -O -L $(git remote get-url $(git remote))/resolve/$(git rev-parse HEAD)/${line}
    done
}

# Clear out any existing checked out models
rm -rf ./models
mkdir models
cd models

# Downloading model for generating vector embeddings
GIT_LFS_SKIP_SMUDGE=1 git clone ${EMBEDDING_MODEL_REPO} --branch main embedding-model 
cd embedding-model
git checkout ${EMBDEDDING_MODEL_COMMIT}
download_lfs_files
cd ..
  
# Downloading LLM model that has been fine tuned to handle instructions/q&a
GIT_LFS_SKIP_SMUDGE=1 git clone ${LLM_MODEL_REPO} --branch main llm-model
cd llm-model
git checkout ${LLM_MODEL_COMMIT}
download_lfs_files
cd ..
