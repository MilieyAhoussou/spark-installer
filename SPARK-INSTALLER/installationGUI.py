import os
import subprocess
import requests
import tarfile
import platform
import tkinter as tk
from tkinter import ttk, messagebox
from tqdm import tqdm
import threading
import queue

SPARK_VERSION = "3.4.1"
SPARK_URL = f"https://archive.apache.org/dist/spark/spark-{SPARK_VERSION}/spark-{SPARK_VERSION}-bin-hadoop3.tgz"
INSTALL_DIR = "/opt/spark"
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
    subprocess.run(['apt-get', 'update'], check=True)
    subprocess.run(['apt-get', 'install', '-y', 'python3'], check=True)
    print("Python a été installé avec succès.")

def install_java():
    """Télécharge et installe OpenJDK"""
    print("Installation de Java...")
    subprocess.run(['apt-get', 'update'], check=True)
    subprocess.run(['apt-get', 'install', '-y', 'openjdk-11-jdk'], check=True)
    print("Java a été installé avec succès.")

def install_winutils():
    """Cette fonction n'est pas nécessaire dans le conteneur"""
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
    
    # Mise à jour du fichier d'environnement
    with open("/etc/environment", "a") as env_file:
        env_file.write(f"\nSPARK_HOME={spark_home}")
        env_file.write(f"\nPATH={spark_home}/bin:$PATH")
    
    print("Variables d'environnement configurées.")

class InstallerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Installateur Apache Spark")
        self.root.geometry("900x700")
        self.root.resizable(False, False)
        
        # Configuration des couleurs
        self.colors = {
            'primary': '#1a237e',  # Bleu profond
            'secondary': '#0d47a1',  # Bleu royal
            'accent': '#ff4081',  # Rose vif
            'background': '#f8f9fa',  # Gris très clair
            'text': '#212121',  # Gris foncé
            'success': '#4CAF50',  # Vert plus vif
            'error': '#c62828',  # Rouge foncé
            'warning': '#f57c00',  # Orange
            'card': '#ffffff'  # Blanc
        }
        
        # Style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configuration du style des boutons
        self.style.configure(
            "Action.TButton",
            padding=20,
            relief="flat",
            background=self.colors['primary'],
            foreground="white",
            font=("Segoe UI", 12, "bold")
        )
        
        self.style.configure(
            "Cancel.TButton",
            padding=20,
            relief="flat",
            background=self.colors['error'],
            foreground="white",
            font=("Segoe UI", 12, "bold")
        )
        
        self.style.configure(
            "TLabel",
            padding=10,
            font=("Segoe UI", 11),
            background=self.colors['background']
        )
        
        self.style.configure(
            "Title.TLabel",
            font=("Segoe UI", 28, "bold"),
            foreground=self.colors['primary'],
            background=self.colors['background']
        )
        
        self.style.configure(
            "TProgressbar",
            thickness=30,
            troughcolor=self.colors['background'],
            background=self.colors['primary']
        )
        
        self.style.configure(
            "Download.TButton",
            padding=20,
            relief="flat",
            background=self.colors['success'],
            foreground="white",
            font=("Segoe UI", 12, "bold")
        )
        
        # Variables
        self.current_step = 0
        self.total_steps = 6
        self.status_queue = queue.Queue()
        
        # Création du conteneur principal avec fond
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Création des widgets
        self.create_widgets()
        
        # Démarrage de la vérification des dépendances
        self.check_dependencies()
        
    def create_widgets(self):
        # En-tête avec fond coloré
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Titre avec icône
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(pady=20)
        
        title_label = ttk.Label(
            title_frame,
            text="Installateur Apache Spark",
            style="Title.TLabel"
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Configuration de votre environnement Spark",
            font=("Segoe UI", 14),
            foreground="#666666"
        )
        subtitle_label.pack(pady=(10, 0))
        
        # Conteneur principal avec ombre
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Barre de progression avec pourcentage
        progress_frame = ttk.Frame(content_frame)
        progress_frame.pack(fill=tk.X, pady=20)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=self.total_steps
        )
        self.progress_bar.pack(fill=tk.X)
        
        self.progress_label = ttk.Label(
            progress_frame,
            text="0%",
            font=("Segoe UI", 12),
            foreground=self.colors['primary']
        )
        self.progress_label.pack(pady=(10, 0))
        
        # État actuel avec icône
        status_frame = ttk.Frame(content_frame)
        status_frame.pack(fill=tk.X, pady=10)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Vérification des dépendances...",
            font=("Segoe UI", 14, "bold"),
            foreground=self.colors['primary']
        )
        self.status_label.pack()
        
        # Bouton de téléchargement avec cadre
        download_frame = ttk.Frame(content_frame, style='Card.TFrame')
        download_frame.pack(fill=tk.X, pady=20, padx=50)
        
        download_title = ttk.Label(
            download_frame,
            text="Apache Spark " + SPARK_VERSION,
            font=("Segoe UI", 16, "bold"),
            foreground=self.colors['primary']
        )
        download_title.pack(pady=(20,5))
        
        download_info = ttk.Label(
            download_frame,
            text="Cliquez sur le bouton ci-dessous pour télécharger Apache Spark",
            font=("Segoe UI", 12),
            foreground=self.colors['text']
        )
        download_info.pack(pady=(0,10))
        
        self.download_button = ttk.Button(
            download_frame,
            text="📥 Télécharger Spark",
            command=self.start_download,
            style="Download.TButton",
            width=25
        )
        self.download_button.pack(pady=(0,20))
        
        # Boutons avec espacement amélioré
        self.button_frame = ttk.Frame(content_frame)
        self.button_frame.pack(pady=30)
        
        self.next_button = ttk.Button(
            self.button_frame,
            text="Suivant",
            command=self.next_step,
            state=tk.DISABLED,
            style="Action.TButton"
        )
        self.next_button.pack(side=tk.RIGHT, padx=15)
        
        self.cancel_button = ttk.Button(
            self.button_frame,
            text="Annuler",
            command=self.cancel_installation,
            style="Cancel.TButton"
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=15)
        
        # Mise à jour de l'interface
        self.update_status()
        
    def update_status(self):
        try:
            while True:
                message = self.status_queue.get_nowait()
                self.log_text.insert(tk.END, message + "\n")
                self.log_text.see(tk.END)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.update_status)
            
    def log_message(self, message):
        self.status_queue.put(message)
        
    def check_dependencies(self):
        def check():
            self.log_message("✓ Vérification des prérequis...")
            java_ok = is_java_installed()
            python_ok = is_python_installed()
            
            if java_ok and python_ok:
                self.log_message("✓ Tous les prérequis sont installés")
                self.download_button.config(state=tk.NORMAL)
            else:
                if not java_ok:
                    self.log_message("❌ Java n'est pas installé")
                if not python_ok:
                    self.log_message("❌ Python n'est pas installé")
                self.download_button.config(state=tk.DISABLED)
                
        threading.Thread(target=check, daemon=True).start()
        
    def next_step(self):
        self.current_step += 1
        self.progress_var.set(self.current_step)
        
        if self.current_step == 1:
            self.status_label.config(text="Téléchargement de Spark...")
            self.next_button.config(state=tk.DISABLED)
            threading.Thread(target=self.download_spark_thread, daemon=True).start()
        elif self.current_step == 2:
            self.status_label.config(text="Installation de WinUtils...")
            self.next_button.config(state=tk.DISABLED)
            threading.Thread(target=self.install_winutils_thread, daemon=True).start()
        elif self.current_step == 3:
            self.status_label.config(text="Extraction de Spark...")
            self.next_button.config(state=tk.DISABLED)
            threading.Thread(target=self.extract_spark_thread, daemon=True).start()
        elif self.current_step == 4:
            self.status_label.config(text="Configuration des variables d'environnement...")
            self.next_button.config(state=tk.DISABLED)
            threading.Thread(target=self.set_env_variables_thread, daemon=True).start()
        elif self.current_step == 5:
            self.status_label.config(text="Installation terminée!")
            self.next_button.config(text="Terminer", command=self.finish_installation)
            
    def download_spark_thread(self):
        if download_spark():
            self.log_message("Téléchargement de Spark réussi.")
            self.next_button.config(state=tk.NORMAL)
        else:
            self.log_message("Erreur lors du téléchargement de Spark.")
            messagebox.showerror("Erreur", "Échec du téléchargement de Spark.")
            
    def install_winutils_thread(self):
        if install_winutils():
            self.log_message("Installation de WinUtils réussie.")
            self.next_button.config(state=tk.NORMAL)
        else:
            self.log_message("Erreur lors de l'installation de WinUtils.")
            messagebox.showerror("Erreur", "Échec de l'installation de WinUtils.")
            
    def extract_spark_thread(self):
        try:
            extract_spark()
            self.log_message("Extraction de Spark réussie.")
            self.next_button.config(state=tk.NORMAL)
        except Exception as e:
            self.log_message(f"Erreur lors de l'extraction: {str(e)}")
            messagebox.showerror("Erreur", "Échec de l'extraction de Spark.")
            
    def set_env_variables_thread(self):
        try:
            set_env_variables()
            self.log_message("Configuration des variables d'environnement réussie.")
            self.next_button.config(state=tk.NORMAL)
        except Exception as e:
            self.log_message(f"Erreur lors de la configuration: {str(e)}")
            messagebox.showerror("Erreur", "Échec de la configuration des variables d'environnement.")
            
    def install_java(self):
        self.log_message("Ouverture de la page de téléchargement de Java...")
        install_java()
        
    def install_python(self):
        self.log_message("Ouverture de la page de téléchargement de Python...")
        install_python()
        
    def cancel_installation(self):
        if messagebox.askyesno("Confirmation", "Voulez-vous vraiment annuler l'installation ?"):
            self.root.quit()
            
    def finish_installation(self):
        messagebox.showinfo("Succès", "L'installation d'Apache Spark est terminée avec succès!")
        self.root.quit()

    def start_download(self):
        """Démarre le téléchargement de Spark"""
        self.download_button.config(state=tk.DISABLED)
        self.status_label.config(text="⬇️ Téléchargement de Spark en cours...")
        self.log_message("Démarrage du téléchargement de Spark...")
        
        def download_thread():
            try:
                if download_spark():
                    self.log_message("✓ Téléchargement terminé avec succès")
                    self.status_label.config(text="✓ Téléchargement terminé !")
                    self.progress_var.set(self.progress_var.get() + 1)
                    self.next_button.config(state=tk.NORMAL)
                else:
                    self.log_message("❌ Erreur lors du téléchargement")
                    self.status_label.config(text="❌ Erreur de téléchargement")
                    self.download_button.config(state=tk.NORMAL)
            except Exception as e:
                self.log_message(f"❌ Erreur : {str(e)}")
                self.status_label.config(text="❌ Erreur de téléchargement")
                self.download_button.config(state=tk.NORMAL)
        
        threading.Thread(target=download_thread, daemon=True).start()

def main():
    root = tk.Tk()
    app = InstallerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
