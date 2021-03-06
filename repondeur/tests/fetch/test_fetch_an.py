from pathlib import Path
from textwrap import dedent

import pytest
import responses
import transaction

from zam_repondeur.fetch.an.amendements import build_url


HERE = Path(__file__)
SAMPLE_DATA_DIR = HERE.parent / "sample_data"


def read_sample_data(basename):
    return (SAMPLE_DATA_DIR / basename).read_text()


class TestFetchAndParseAll:
    @responses.activate
    def test_simple_amendements(self, lecture_an, app):
        from zam_repondeur.fetch.an.amendements import fetch_and_parse_all

        responses.add(
            responses.GET,
            build_url(lecture_an),
            body=read_sample_data("an/269/liste.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            build_url(lecture_an, 177),
            body=read_sample_data("an/269/177.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            build_url(lecture_an, 270),
            body=read_sample_data("an/269/270.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            build_url(lecture_an, 723),
            body=read_sample_data("an/269/723.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            build_url(lecture_an, 135),
            body=read_sample_data("an/269/135.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            build_url(lecture_an, 192),
            body=read_sample_data("an/269/192.xml"),
            status=200,
        )

        amendements, created, errored = fetch_and_parse_all(lecture=lecture_an)

        assert len(amendements) == 5

        assert amendements[0].num == 177
        assert amendements[0].position == 1
        assert amendements[0].id_discussion_commune is None
        assert amendements[0].id_identique == 20386

        assert amendements[1].num == 270
        assert amendements[1].position == 2
        assert amendements[1].id_discussion_commune is None
        assert amendements[1].id_identique == 20386

        assert amendements[2].num == 723
        assert amendements[2].position == 3
        assert amendements[2].id_discussion_commune is None
        assert amendements[2].id_identique is None

        assert amendements[3].num == 135
        assert amendements[3].position == 4
        assert amendements[3].id_discussion_commune is None
        assert amendements[3].id_identique is None

        assert amendements[4].num == 192
        assert amendements[4].position == 5
        assert amendements[4].id_discussion_commune is None
        assert amendements[4].id_identique == 20439

        assert created == 5
        assert errored == []

    @responses.activate
    def test_sous_amendements(self, app):
        from zam_repondeur.fetch.an.amendements import fetch_and_parse_all
        from zam_repondeur.models import Lecture

        with transaction.manager:
            lecture = Lecture.create(
                chambre="an",
                session="15",
                num_texte=911,
                titre="Titre lecture",
                organe="PO717460",
                dossier_legislatif="Titre dossier legislatif",
            )

        responses.add(
            responses.GET,
            build_url(lecture),
            body=read_sample_data("an/911/liste.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            build_url(lecture, 347),
            body=read_sample_data("an/911/347.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            build_url(lecture, 2482),
            body=read_sample_data("an/911/2482.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            build_url(lecture, 2512),
            body=read_sample_data("an/911/2512.xml"),
            status=200,
        )

        amendements, created, errored = fetch_and_parse_all(lecture=lecture)

        assert len(amendements) == 3

        assert amendements[0].num == 347
        assert amendements[0].position == 1
        assert amendements[0].id_discussion_commune == 3448
        assert amendements[0].id_identique == 8496

        assert amendements[1].num == 2482
        assert amendements[1].position == 2
        assert amendements[1].id_discussion_commune is None
        assert amendements[1].id_identique is None

        assert amendements[2].num == 2512
        assert amendements[2].position == 3
        assert amendements[2].id_discussion_commune is None
        assert amendements[1].id_identique is None

        for amendement in amendements[1:]:
            assert amendement.parent is amendements[0]
            assert amendement.parent_pk == amendements[0].pk

        assert created == 3
        assert errored == []

    @responses.activate
    def test_with_404(self, lecture_an, app):
        from zam_repondeur.fetch.an.amendements import fetch_and_parse_all

        responses.add(
            responses.GET,
            build_url(lecture_an),
            body=read_sample_data("an/269/liste.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            build_url(lecture_an, 177),
            body=read_sample_data("an/269/177.xml"),
            status=200,
        )
        responses.add(responses.GET, build_url(lecture_an, 270), status=404)
        responses.add(
            responses.GET,
            build_url(lecture_an, 723),
            body=read_sample_data("an/269/723.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            build_url(lecture_an, 135),
            body=read_sample_data("an/269/135.xml"),
            status=200,
        )
        responses.add(
            responses.GET,
            build_url(lecture_an, 192),
            body=read_sample_data("an/269/192.xml"),
            status=200,
        )

        amendements, created, errored = fetch_and_parse_all(lecture=lecture_an)

        assert len(amendements) == 4
        assert amendements[0].num == 177
        assert amendements[1].num == 723
        assert amendements[2].num == 135
        assert amendements[3].num == 192

        assert [amdt.position for amdt in amendements] == list(range(1, 5))
        assert created == 4
        assert errored == ["270"]


class TestFetchAmendements:
    @responses.activate
    def test_simple_amendements(self, lecture_an, app):
        from zam_repondeur.fetch.an.amendements import fetch_amendements

        responses.add(
            responses.GET,
            build_url(lecture_an),
            body=read_sample_data("an/269/liste.xml"),
            status=200,
        )

        items = fetch_amendements(lecture=lecture_an)

        assert len(items) == 5
        assert items[0] == {
            "@alineaLabel": "S",
            "@auteurGroupe": "Les Républicains",
            "@auteurLabel": "M. DOOR",
            "@auteurLabelFull": "M. DOOR Jean-Pierre",
            "@discussionCommune": "",
            "@discussionCommuneAmdtPositon": "",
            "@discussionCommuneSsAmdtPositon": "",
            "@discussionIdentique": "20386",
            "@discussionIdentiqueAmdtPositon": "debut",
            "@discussionIdentiqueSsAmdtPositon": "",
            "@missionLabel": "",
            "@numero": "177",
            "@parentNumero": "",
            "@place": "Article 3",
            "@position": "001/772",
            "@sort": "Rejeté",
        }

    @responses.activate
    def test_only_one_amendement(self, lecture_an, app):
        from zam_repondeur.fetch.an.amendements import fetch_amendements

        responses.add(
            responses.GET,
            build_url(lecture_an),
            body=dedent(
                """\
            <?xml version="1.0" encoding="UTF-8"?>
            <amdtsParOrdreDeDiscussion  bibard="4072"  bibardSuffixe=""  organe="AN"
              legislature="14"  titre="PLFSS 2017"
               type="projet de loi de financement de la sécurité sociale">
              <amendements>
                <amendement  place="Article 3"  numero="177"  sort="Rejeté"
                    parentNumero=""  auteurLabel="M. DOOR"
                    auteurLabelFull="M. DOOR Jean-Pierre"
                    auteurGroupe="Les Républicains"  alineaLabel="S"  missionLabel=""
                    discussionCommune=""  discussionCommuneAmdtPositon=""
                    discussionCommuneSsAmdtPositon=""  discussionIdentique="20386"
                    discussionIdentiqueAmdtPositon="debut"
                    discussionIdentiqueSsAmdtPositon=""  position="001/772"  />
              </amendements>
            </amdtsParOrdreDeDiscussion>
            """
            ),
            status=200,
        )

        items = fetch_amendements(lecture=lecture_an)

        assert isinstance(items, list)
        assert items[0] == {
            "@alineaLabel": "S",
            "@auteurGroupe": "Les Républicains",
            "@auteurLabel": "M. DOOR",
            "@auteurLabelFull": "M. DOOR Jean-Pierre",
            "@discussionCommune": "",
            "@discussionCommuneAmdtPositon": "",
            "@discussionCommuneSsAmdtPositon": "",
            "@discussionIdentique": "20386",
            "@discussionIdentiqueAmdtPositon": "debut",
            "@discussionIdentiqueSsAmdtPositon": "",
            "@missionLabel": "",
            "@numero": "177",
            "@parentNumero": "",
            "@place": "Article 3",
            "@position": "001/772",
            "@sort": "Rejeté",
        }

    @responses.activate
    def test_list_not_found(self, lecture_an, app):
        from zam_repondeur.fetch.an.amendements import fetch_amendements, NotFound

        responses.add(responses.GET, build_url(lecture_an), status=404)

        with pytest.raises(NotFound):
            fetch_amendements(lecture=lecture_an)


class TestFetchAmendement:
    @responses.activate
    def test_simple_amendement(self, lecture_an, app):
        from zam_repondeur.fetch.an.amendements import fetch_amendement

        responses.add(
            responses.GET,
            build_url(lecture_an, 177),
            body=read_sample_data("an/269/177.xml"),
            status=200,
        )

        amendement, created = fetch_amendement(
            lecture=lecture_an, numero=177, position=1
        )

        assert amendement.lecture == lecture_an
        assert amendement.num == 177
        assert amendement.rectif == 0
        assert amendement.auteur == "Door Jean-Pierre"
        assert amendement.matricule == "267289"
        assert amendement.date_depot is None
        assert amendement.sort == "rejeté"
        assert amendement.position == 1
        assert amendement.id_discussion_commune is None
        assert amendement.id_identique is None
        assert amendement.parent is None
        assert amendement.dispositif == "<p>Supprimer cet article.</p>"
        assert amendement.objet == (
            "<p>Amendement d&#8217;appel.</p>\n<p>Pour couvrir les d&#233;passements "
            "attendus de l&#8217;ONDAM pour 2016, cet article pr&#233;voit un "
            "pr&#233;l&#232;vement de 200 millions d&#8217;&#8364; sur les fonds de "
            "roulement de l&#8217;association nationale pour la formation permanente "
            "du personnel hospitalier (ANFH) et du fonds pour l&#8217;emploi "
            "hospitalier (FEH) pour financer le <span>fonds pour la modernisation des "
            "&#233;tablissements de sant&#233; publics et priv&#233;s</span>(FMESPP) "
            "en remplacement de cr&#233;dit de l&#8217;ONDAM. Il participe donc &#224; "
            "la pr&#233;sentation insinc&#232;re de la construction de l&#8217;ONDAM, "
            "d&#233;nonc&#233;e par le Comit&#233; d&#8217;alerte le 12 octobre "
            "dernier.</p>"
        )
        assert amendement.resume is None
        assert amendement.avis is None
        assert amendement.observations is None
        assert amendement.reponse is None

    @responses.activate
    def test_fetch_amendement_gouvernement(self, lecture_an):
        from zam_repondeur.fetch.an.amendements import fetch_amendement

        responses.add(
            responses.GET,
            build_url(lecture_an, 723),
            body=read_sample_data("an/269/723.xml"),
            status=200,
        )

        amendement, created = fetch_amendement(
            lecture=lecture_an, numero=723, position=1
        )

        assert amendement.gouvernemental is True
        assert amendement.groupe == ""

    @responses.activate
    def test_fetch_amendement_commission(self, lecture_an):
        from zam_repondeur.fetch.an.amendements import fetch_amendement

        responses.add(
            responses.GET,
            build_url(lecture_an, 135),
            body=read_sample_data("an/269/135.xml"),
            status=200,
        )

        amendement, created = fetch_amendement(
            lecture=lecture_an, numero=135, position=1
        )

        assert amendement.gouvernemental is False
        assert amendement.auteur == "Bapt Gérard"
        assert amendement.groupe == ""

    @responses.activate
    def test_fetch_sous_amendement(self, lecture_an, app):
        from zam_repondeur.fetch.an.amendements import fetch_amendement

        responses.add(
            responses.GET,
            build_url(lecture_an, 155),
            body=read_sample_data("an/269/155.xml"),
            status=200,
        )

        responses.add(
            responses.GET,
            build_url(lecture_an, 941),
            body=read_sample_data("an/269/941.xml"),
            status=200,
        )

        amendement1, created = fetch_amendement(
            lecture=lecture_an, numero=155, position=1
        )
        assert created
        amendement2, created = fetch_amendement(
            lecture=lecture_an, numero=941, position=1
        )
        assert created

        assert amendement2.parent is amendement1

    @responses.activate
    def test_fetch_amendement_sort_nil(self, lecture_an, app):
        from zam_repondeur.fetch.an.amendements import fetch_amendement

        responses.add(
            responses.GET,
            build_url(lecture_an, 38),
            body=read_sample_data("an/269/38.xml"),
            status=200,
        )

        amendement, created = fetch_amendement(
            lecture=lecture_an, numero=38, position=1
        )

        assert amendement.sort == ""

    @responses.activate
    def test_fetch_amendement_apres(self, lecture_an, app):
        from zam_repondeur.fetch.an.amendements import fetch_amendement

        responses.add(
            responses.GET,
            build_url(lecture_an, 192),
            body=read_sample_data("an/269/192.xml"),
            status=200,
        )

        amendement, created = fetch_amendement(
            lecture=lecture_an, numero=192, position=1
        )

        assert amendement.article.type == "article"
        assert amendement.article.num == "8"
        assert amendement.article.mult == ""
        assert amendement.article.pos == "après"

    @responses.activate
    def test_fetch_amendement_not_found(self, lecture_an, app):
        from zam_repondeur.fetch.an.amendements import fetch_amendement, NotFound

        responses.add(responses.GET, build_url(lecture_an, 177), status=404)

        with pytest.raises(NotFound):
            fetch_amendement(lecture=lecture_an, numero=177, position=1)


class TestFetchAmendementAgain:
    @responses.activate
    def test_response_is_preserved(self, lecture_an, app):
        from zam_repondeur.fetch.an.amendements import fetch_amendement

        responses.add(
            responses.GET,
            build_url(lecture_an, 177),
            body=read_sample_data("an/269/177.xml"),
            status=200,
        )

        # Let's fetch a new amendement
        amendement1, created = fetch_amendement(
            lecture=lecture_an, numero=177, position=1
        )
        assert created

        # Now let's add a response
        amendement1.avis = "Favorable"
        amendement1.observations = "Observations"
        amendement1.reponse = "Réponse"

        # And fetch the same amendement again
        amendement2, created = fetch_amendement(
            lecture=lecture_an, numero=177, position=1
        )
        assert not created
        assert amendement2 is amendement1

        # The response has been preserved
        assert amendement2.avis == "Favorable"
        assert amendement2.observations == "Observations"
        assert amendement2.reponse == "Réponse"

    @responses.activate
    def test_article_has_changed(self, lecture_an, app):
        from zam_repondeur.fetch.an.amendements import fetch_amendement

        responses.add(
            responses.GET,
            build_url(lecture_an, 177),
            body=read_sample_data("an/269/177.xml"),
            status=200,
        )

        amendement1, created = fetch_amendement(
            lecture=lecture_an, numero=177, position=1
        )
        assert created

        amendement1.article = None  # let's change the article

        amendement2, created = fetch_amendement(
            lecture=lecture_an, numero=177, position=1
        )
        assert not created
        assert amendement2 is amendement1

    @responses.activate
    def test_parent_has_changed(self, lecture_an, app):
        from zam_repondeur.fetch.an.amendements import fetch_amendement
        from zam_repondeur.models import DBSession

        responses.add(
            responses.GET,
            build_url(lecture_an, 155),
            body=read_sample_data("an/269/155.xml"),
            status=200,
        )

        responses.add(
            responses.GET,
            build_url(lecture_an, 941),
            body=read_sample_data("an/269/941.xml"),
            status=200,
        )

        parent1, created = fetch_amendement(lecture=lecture_an, numero=155, position=1)
        assert created

        child1, created = fetch_amendement(lecture=lecture_an, numero=941, position=1)
        assert created

        assert child1.parent is parent1
        assert child1.parent_pk == parent1.pk

        child1.parent = None  # let's change the parent amendement
        DBSession.flush()

        parent2, created = fetch_amendement(lecture=lecture_an, numero=155, position=1)
        assert not created
        assert parent2 is parent1

        child2, created = fetch_amendement(lecture=lecture_an, numero=941, position=1)
        assert not created
        assert child2 is child1

        assert child2.parent_pk == parent2.pk
        assert child2.parent is parent2


@pytest.mark.parametrize(
    "division,type_,num,mult,pos",
    [
        (
            {
                "titre": "pour un État au service d’une société de confiance.",
                "divisionDesignation": "TITRE",
                "type": "TITRE",
                "avantApres": "A",
                "divisionRattache": "TITRE",
                "articleAdditionnel": {
                    "@xsi:nil": "true",
                    "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                },
                "divisionAdditionnelle": {
                    "@xsi:nil": "true",
                    "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
                },
                "urlDivisionTexteVise": "/15/textes/0575.asp#D_pour_un_Etat_au_service_dune_societe_d",  # noqa
            },
            "titre",
            "",
            "",
            "",
        )
    ],
)
def test_parse_division(division, type_, num, mult, pos):
    from zam_repondeur.fetch.an.amendements import parse_division

    assert parse_division(division) == (type_, num, mult, pos)
