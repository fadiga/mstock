# mstock

**M. Stock** — logiciel de gestion de stock, inventaire et facturation pour commerces (v6.3).

Application bureau PyQt4 orientée boutique : suivi multi-magasin des entrées, sorties, inventaires, commandes fournisseurs et facturation.

## Fonctionnalités

- Gestion des produits, catégories et magasins
- Entrées et sorties de stock avec calcul automatique du restant
- Inventaire et état du stock en temps réel
- Commandes fournisseurs
- Facturation (facture et proforma)
- Tableau de bord avec alertes
- Rôles administrateur avec menus restreints
- Packaging Windows (py2exe + NSIS)

## Stack technique

- Python · PyQt4
- Peewee ORM · SQLite
- ReportLab (PDF) · export Excel

## Prérequis

Ce projet dépend de la librairie interne **Common** / **GCommon** (non incluse dans ce dépôt), à placer au même niveau que le répertoire du projet.

## Installation

```bash
# Placer Common/ au même niveau que mstock/
python main.py
```

## Structure

```
mstock/
├── main.py
├── models.py
├── configuration.py
├── ui/              # Vues : dashboard, stock, factures, commandes…
├── locale/
└── setup-win.py     # Build Windows
```

## Auteur

[Ibrahima Fadiga](https://github.com/fadiga) — Bamako, Mali
