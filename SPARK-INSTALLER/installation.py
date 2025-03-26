import os
import subprocess
import requests
from tqdm import tqdm

SPARK_VERSION = "3.4.1"
SPARK_URL = f"https://archive.apache.org/dist/spark/spark-{SPARK_VERSION}/spark-{SPARK_VERSION}-bin-hadoop3.tgz"
INSTALL_DIR = "/opt/spark"

def check_prerequisites():
    """Vérifie si Java et Python sont installés"""
    print("Vérification des prérequis...")
    
    # Vérifier Java
    try:
        subprocess.run(['java', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✓ Java est installé")
    except subprocess.CalledProcessError:
        print("❌ Java n'est pas installé")
        return False

    # Vérifier Python
    try:
        subprocess.run(['python', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✓ Python est installé")
    except subprocess.CalledProcessError:
        print("❌ Python n'est pas installé")
        return False
    
    return True

def download_spark():
    """Télécharge Apache Spark"""
    print(f"\nTéléchargement de Apache Spark {SPARK_VERSION}...")
    os.makedirs(INSTALL_DIR, exist_ok=True)
    
    try:
        response = requests.get(SPARK_URL, stream=True)
        if response.status_code != 200:
            print(f"❌ Erreur lors du téléchargement. Status code: {response.status_code}")
            return False
            
        spark_archive = os.path.join(INSTALL_DIR, 'spark.tgz')
        total_size = int(response.headers.get('Content-Length', 0))
        
        with open(spark_archive, "wb") as file, tqdm(
            desc="Téléchargement", 
            total=total_size, 
            unit='B', 
            unit_scale=True
        ) as bar:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
                bar.update(len(chunk))
        
        print("✓ Téléchargement terminé")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement : {str(e)}")
        return False

def extract_spark():
    """Extrait l'archive Spark"""
    print("\nExtraction de Spark...")
    try:
        import tarfile
        with tarfile.open(os.path.join(INSTALL_DIR, 'spark.tgz'), 'r:gz') as tar_ref:
            tar_ref.extractall(INSTALL_DIR)
        os.remove(os.path.join(INSTALL_DIR, 'spark.tgz'))
        print("✓ Extraction terminée")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de l'extraction : {str(e)}")
        return False

def setup_environment():
    """Configure les variables d'environnement"""
    print("\nConfiguration des variables d'environnement...")
    try:
        spark_home = os.path.join(INSTALL_DIR, f"spark-{SPARK_VERSION}-bin-hadoop3")
        
        # Ajouter les variables d'environnement
        with open(os.path.expanduser("~/.bashrc"), "a") as f:
            f.write(f'\nexport SPARK_HOME={spark_home}')
            f.write(f'\nexport PATH=$PATH:{spark_home}/bin')
        
        print("✓ Variables d'environnement configurées")
        print(f"\nPour activer les changements, exécutez: source ~/.bashrc")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la configuration : {str(e)}")
        return False

def main():
    print("=== Installation de Apache Spark ===\n")
    
    if not check_prerequisites():
        print("\n❌ Veuillez installer les prérequis manquants avant de continuer.")
        return
    
    if not download_spark():
        return
        
    if not extract_spark():
        return
        
    if not setup_environment():
        return
        
    print("\n✓ Installation terminée avec succès!")
    print(f"Spark est installé dans: {INSTALL_DIR}")

if __name__ == "__main__":
    main()
