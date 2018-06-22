import json

import pytest


@pytest.fixture
def amendements():
    from zam_aspirateur.amendements.models import Amendement

    return [
        Amendement(
            chambre="senat",
            session="2017-2018",
            num_texte=63,
            subdiv_type="article",
            subdiv_num="1",
            alinea="",
            num=42,
            auteur="M. DUPONT",
            groupe="RDSE",
            matricule="000000",
            dispositif="<p>L'article 1 est supprimé.</p>",
            objet="<p>Cet article va à l'encontre du principe d'égalité.</p>",
            resume="Suppression de l'article",
        ),
        Amendement(
            chambre="senat",
            session="2017-2018",
            num_texte=63,
            subdiv_type="article",
            subdiv_num="1",
            subdiv_pos="avant",
            alinea="",
            num=57,
            auteur="M. DURAND",
            groupe="Les Républicains",
            matricule="000001",
            objet="baz",
            dispositif="qux",
        ),
        Amendement(
            chambre="senat",
            session="2017-2018",
            num_texte=63,
            subdiv_type="article",
            subdiv_num="7",
            subdiv_mult="bis",
            alinea="",
            num=21,
            auteur="M. MARTIN",
            groupe=None,
            matricule="000002",
            objet="quux",
            dispositif="quuz",
        ),
        Amendement(
            chambre="senat",
            session="2017-2018",
            num_texte=63,
            subdiv_type="article",
            subdiv_num="1",
            alinea="",
            num=43,
            auteur="M. JEAN",
            groupe="Les Indépendants",
            matricule="000003",
            objet="corge",
            dispositif="grault",
        ),
    ]


FIELDS = [
    "chambre",
    "session",
    "num_texte",
    "subdiv_type",
    "subdiv_num",
    "subdiv_mult",
    "subdiv_pos",
    "subdiv_titre",
    "subdiv_contenu",
    "alinea",
    "num",
    "rectif",
    "auteur",
    "matricule",
    "groupe",
    "date_depot",
    "sort",
    "position",
    "discussion_commune",
    "identique",
    "dispositif",
    "objet",
    "resume",
    "avis",
    "observations",
    "reponse",
]


def test_write_csv(amendements, tmpdir):
    from zam_aspirateur.amendements.writer import write_csv

    filename = str(tmpdir.join("test.csv"))

    nb_rows = write_csv(amendements, filename)

    with open(filename, "r", encoding="utf-8") as f_:
        lines = f_.read().splitlines()
    header, *rows = lines
    assert header == ";".join(FIELDS)

    assert len(rows) == nb_rows == 4

    assert (
        rows[0]
        == "senat;2017-2018;63;article;1;;;;;;42;0;M. DUPONT;000000;RDSE;;;;;;<p>L'article 1 est supprimé.</p>;<p>Cet article va à l'encontre du principe d'égalité.</p>;Suppression de l'article;;;"  # noqa
    )


def test_write_json_for_viewer(amendements, tmpdir):
    from zam_aspirateur.amendements.writer import write_json_for_viewer

    TITLE = "Projet Loi de Financement de la Sécurité Sociale 2018"

    filename = str(tmpdir.join("test.json"))

    write_json_for_viewer(1, TITLE, amendements, filename)

    with open(filename, "r", encoding="utf-8") as f_:
        data = json.load(f_)

    assert data == [
        {
            "idProjet": 1,
            "libelle": "Projet Loi de Financement de la Sécurité Sociale 2018",
            "list": [
                {
                    "id": 1,
                    "pk": "article-1",
                    "etat": "",
                    "multiplicatif": "",
                    "titre": "TODO",
                    "jaune": "jaune-1.pdf",
                    "document": "article-1.pdf",
                    "amendements": [
                        {
                            "id": 42,
                            "pk": "000042",
                            "etat": "",
                            "gouvernemental": False,
                            "auteur": "M. DUPONT",
                            "groupe": {"libelle": "RDSE", "couleur": "#a38ebc"},
                            "document": "000042-00.pdf",
                            "dispositif": "<p>L'article 1 est supprimé.</p>",
                            "objet": "<p>Cet article va à l'encontre du principe d'égalité.</p>",  # noqa
                            "resume": "Suppression de l'article",
                        },
                        {
                            "id": 43,
                            "pk": "000043",
                            "etat": "",
                            "gouvernemental": False,
                            "auteur": "M. JEAN",
                            "groupe": {
                                "libelle": "Les Indépendants",
                                "couleur": "#30bfe9",
                            },
                            "document": "000043-00.pdf",
                            "dispositif": "grault",
                            "objet": "corge",
                            "resume": "",
                        },
                    ],
                },
                {
                    "id": 1,
                    "pk": "article-1av",
                    "etat": "av",
                    "multiplicatif": "",
                    "titre": "TODO",
                    "jaune": "jaune-1av.pdf",
                    "document": "article-1av.pdf",
                    "amendements": [
                        {
                            "id": 57,
                            "pk": "000057",
                            "etat": "",
                            "gouvernemental": False,
                            "auteur": "M. DURAND",
                            "groupe": {
                                "libelle": "Les Républicains",
                                "couleur": "#2011e8",
                            },
                            "document": "000057-00.pdf",
                            "dispositif": "qux",
                            "objet": "baz",
                            "resume": "",
                        }
                    ],
                },
                {
                    "id": 7,
                    "pk": "article-7bis",
                    "etat": "",
                    "multiplicatif": "bis",
                    "titre": "TODO",
                    "jaune": "jaune-7bis.pdf",
                    "document": "article-7bis.pdf",
                    "amendements": [
                        {
                            "id": 21,
                            "pk": "000021",
                            "etat": "",
                            "gouvernemental": False,
                            "auteur": "M. MARTIN",
                            "groupe": {"libelle": "", "couleur": "#ffffff"},
                            "document": "000021-00.pdf",
                            "dispositif": "quuz",
                            "objet": "quux",
                            "resume": "",
                        }
                    ],
                },
            ],
        }
    ]
