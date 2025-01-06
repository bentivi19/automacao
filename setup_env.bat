@echo off
echo Limpando cache do pip e configurando novo ambiente...

:: Desativa qualquer ambiente virtual ativo
call deactivate 2>nul

:: Limpa o cache do pip
echo Limpando cache do pip...
pip cache purge

:: Remove ambiente virtual anterior se existir
if exist "venv" (
    echo Removendo ambiente virtual anterior...
    rmdir /s /q venv
)

:: Cria novo ambiente virtual
echo Criando novo ambiente virtual...
python -m venv venv

:: Ativa o novo ambiente virtual
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

:: Atualiza pip
echo Atualizando pip...
python -m pip install --upgrade pip

:: Instala poetry no novo ambiente
echo Instalando poetry...
pip install poetry

:: Instala dependências do projeto usando poetry
echo Instalando dependências do projeto...
poetry install

echo.
echo Ambiente configurado com sucesso!
echo Para ativar o ambiente virtual, use: venv\Scripts\activate.bat
pause
