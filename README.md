# MES-Term-Project
Name TBD. Multi-media expert system for diagnosing tomato plant ailments and suggesting best next steps.

## Setting up & running the project

### UV
**Prerequisite:** [uv](https://docs.astral.sh/uv/getting-started/installation/)

**Clone**:

```bash
git clone https://github.com/Jaefae/MES-Term-Project.git
cd MES-Term-Project
```

**Run** (from repo root, first time fetches dependencies):

```bash
uv run streamlit run src/app.py
```

The website should be viewable at [localhost:8501](http://localhost:8501), but check the port used when streamlit is ran.

### Manual

**Prerequisite:** Python 3.13+

**Clone**:

```bash
git clone https://github.com/Jaefae/MES-Term-Project.git
cd MES-Term-Project
```

**Installing streamlit** (using pip):

```bash
pip install streamlit
```

**Running the project** (from repo root):

```bash
streamlit run src/app.py
```

The website should be viewable at [localhost:8501](http://localhost:8501), but check the port used when streamlit is ran.
