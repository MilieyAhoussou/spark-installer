# Spark Installer for Windows

Ce projet fournit un script Python pour l'installation automatisée d'Apache Spark sur Windows, avec les dépendances nécessaires telles que **Java**, **Python**, et **winutils**.

## Fonctionnalités

- Téléchargement et installation automatique de **Java** et **Python** si non présents.
- Téléchargement, extraction, et installation d'Apache Spark.
- Configuration des variables d'environnement nécessaires.
- Téléchargement et installation de **winutils.exe** pour Hadoop sur Windows.

## Prérequis

Avant d'exécuter le script, assurez-vous d'avoir les éléments suivants :
- **Python** installé sur votre machine (si non installé, le script peut l'installer pour vous).
- **Java** installé (si non installé, le script peut l'installer pour vous).

## Installation
Pour l'instant l'installation ce fait avec un script python, mais dans les version avenir windows pourra lancer ne fichier d'installation natif.
( Ce script est pas parfait il peut comporter des erreurs )

1. Clonez ce dépôt ou téléchargez les fichiers.

   git clone https://github.com/MilieyAhoussou
   cd spark-installer

2.Exécutez le script install_spark.py :

python install_spark.py
Le script va :

Télécharger et installer Apache Spark.

Installer Java et Python si nécessaire.

Configurer les variables d'environnement pour Spark et Hadoop.

Télécharger winutils.exe nécessaire à Hadoop sous Windows.

Contribuer
Si vous souhaitez contribuer à ce projet, vous pouvez forker ce dépôt, apporter vos modifications et soumettre une pull request. Assurez-vous de suivre les bonnes pratiques de Git pour vos commits.