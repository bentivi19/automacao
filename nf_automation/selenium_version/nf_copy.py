import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def copy_nf():
    # Configuração do driver
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
    
    try:
        # Navega para a página
        driver.get("sua_url_aqui")
        
        # Lógica de cópia das NFs
        pass
        
    finally:
        driver.quit()
