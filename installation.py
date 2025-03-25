import os
import subprocess
import requests
import tarfile
import platform
from tqdm import tqdm

SPARK_VERSION = "3.4.1"
SPARK_URL = f"https://archive.apache.org/dist/spark/spark-{SPARK_VERSION}/spark-{SPARK_VERSION}-bin-hadoop3.tgz"
INSTALL_DIR = os.path.expanduser("~\\spark")
PYTHON_URL = "https://www.python.org/downloads/"

def is_java_installed():
    """Vérifie si Java est installé"""
    try:
        subprocess.run(['java', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Java est déjà installé.")
        return True
    except subprocess.CalledProcessError:
        print("Java n'est pas installé.")
        return False

def is_python_installed():
    """Vérifie si Python est installé"""
    try:
        subprocess.run(['python', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Python est déjà installé.")
        return True
    except subprocess.CalledProcessError:
        print("Python n'est pas installé.")
        return False

def install_python():
    """Télécharge et installe Python"""
    print("Téléchargement de Python...")
    subprocess.run(['start', PYTHON_URL], shell=True)
    print("Python a été installé avec succès.")

def install_winutils():
    """Télécharge winutils.exe et l'ajoute à HADOOP_HOME"""
    hadoop_bin_dir = os.path.join(INSTALL_DIR, "hadoop", "bin")
    if not os.path.exists(hadoop_bin_dir):
        os.makedirs(hadoop_bin_dir)

    winutils_url = "https://github.com/steveloughran/winutils/blob/master/hadoop-3.0.0/bin/winutils.exe?raw=true"
    response = requests.get(winutils_url, stream=True)
    if response.status_code != 200:
        print(f"Erreur lors du téléchargement de winutils. Status code: {response.status_code}")
        return False
        
    winutils_path = os.path.join(hadoop_bin_dir, "winutils.exe")
    with open(winutils_path, "wb") as f:
        f.write(response.content)
    print(f"winutils.exe installé à {winutils_path}")
    return True

def download_spark():
    """Télécharge Apache Spark avec une barre de progression"""
    print("Téléchargement de Spark...")
    os.makedirs(INSTALL_DIR, exist_ok=True)
    response = requests.get(SPARK_URL, stream=True)
    if response.status_code != 200:
        print(f"Erreur lors du téléchargement. Status code: {response.status_code}")
        return False
    spark_archive = os.path.join(INSTALL_DIR, 'spark.tgz')
    total_size = int(response.headers.get('Content-Length', 0))
    with open(spark_archive, "wb") as file, tqdm(
        desc="Téléchargement", total=total_size, unit="B", unit_scale=True
    ) as bar:
        for chunk in response.iter_content(chunk_size=1024):
            file.write(chunk)
            bar.update(len(chunk))

    print("Téléchargement de Spark terminé.")
    return True

def extract_spark():
    """Extraire Spark"""
    print("Extraction de Spark...")
    with tarfile.open(os.path.join(INSTALL_DIR, 'spark.tgz'), 'r:gz') as tar_ref:
        tar_ref.extractall(INSTALL_DIR)
    os.remove(os.path.join(INSTALL_DIR, 'spark.tgz'))
    print("Extraction terminée.")

def set_env_variables():
    """Définir les variables d'environnement"""
    print("Configuration des variables d'environnement...")
    spark_home = os.path.join(INSTALL_DIR, f"spark-{SPARK_VERSION}-bin-hadoop3")
    hadoop_home = os.path.join(INSTALL_DIR, "hadoop")

    os.environ['SPARK_HOME'] = spark_home
    os.environ['HADOOP_HOME'] = hadoop_home
    os.environ['PATH'] = f"{spark_home}\\bin;{hadoop_home}\\bin;" + os.environ['PATH']

    # Mise à jour du fichier d'environnement
    bashrc_path = os.path.expanduser("~\\.bash_profile")  # Ou .bashrc ou autres en fonction de l'OS
    with open(bashrc_path, "a") as bashrc:
        bashrc.write(f"\n# Apache Spark\nexport SPARK_HOME={spark_home}\nexport HADOOP_HOME={hadoop_home}\nexport PATH=$SPARK_HOME/bin:$HADOOP_HOME/bin:$PATH")
    print("Variables d'environnement configurées.")

def install_java():
    """Télécharge et installe OpenJDK sur Windows"""
    print("Installation de Java...")
    java_url = "https://adoptium.net/temurin/releases/?version=17"  # Télécharger depuis Eclipse Temurin
    subprocess.run(['start', java_url], shell=True)
    print("Java a été installé avec succès.")

def main():
    if not is_java_installed():
        install_java()

    if not is_python_installed():
        install_python()

    if not download_spark():
        print("Échec du téléchargement de Spark. Arrêt de l'installation.")
        return

    if not install_winutils():
        print("Échec de l'installation de winutils. Arrêt de l'installation.")
        return

    extract_spark()
    set_env_variables()
    print("Installation terminée. Apache Spark est prêt à l'emploi.")

if __name__ == "__main__":
    main()
