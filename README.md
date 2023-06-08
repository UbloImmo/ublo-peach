# Install

- Make sure you have python3 installed
- Run `./setup.sh`
- Copy `./.streamlit/secrets.template.toml` to `./.streamlit/secrets.toml` and fill it

# Run

| First run will be slower as the langchain index has to be created first

- Run `source .venv/bin/activate`
- Run `streamlit run site.py`

# What it does

- Ask a question
- A model rewords the question (refine.py) => "text-davinci-003"
- A model turns the refine question in embed (embeds.py) => "text-embedding-ada-002"
- The embedings are sent to the indexer (indexer.py) => "pinecone"
- The indexer responds with matches
- The matches are passed with the question => "gpt-3.5" | "gpt-4" + system + history
- The model responds
