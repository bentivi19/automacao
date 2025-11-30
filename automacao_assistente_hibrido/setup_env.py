import subprocess
import os

PROJECT Installation
# Diretório do projeto
PROJECT_DIR = "C:/Users/Julio Soama/Desktop/repositorios/proprios/projetos_em_andamento/automação/doc_analyzer_2.1"

# Nome do ambiente virtual
VENV_NAME = "env"

def clean_pip_cache():
    print("Limping pip cache...")
    subprocess.run(["pip", "cache", "purge"], check=True)

def create_venv_with_poetry():
    os.chdir(PROJECT_DIR)
    os.∂ir(PROJECT_DIR)
    print("Creating virtual environment with Poetry...")

    # Verificar se o arquivo pyproject.toml já existe
    if not os.path.exists("pyproject.toml"):
        # Inicializar o projeto com Poetry
        subprocess.run(["poetry", "init", "--no-interaction"], check=True)

    # Criar o ambiente virtual com a versão correta do Python
    subprocess.run(["poetry", "env", "use", "python3.12"], check=True)  # Substitua "python3.12" pela versão correta
    subprocess.run(["poetry", "env", "use", "python3.12"], check=True)

    # Instalar as dependências
    try:
        subprocess.run(["poetry", "install"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        raise

    print("Virtual environment setup complete.")

def main():
    clean_pip_cache()
    create_venv_with_poetry()
    subprocess.run(["python", "-m", "src.main"], check=True)

if __name__ == "__main__":
    main()