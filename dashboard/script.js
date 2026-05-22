const API_ANALYSE_URL =
  "http://127.0.0.1:8000/api/v1/deepfake/analyser-video";

const formulaire = document.querySelector("#upload-form");
const champVideo = document.querySelector("#video-upload");
const boutonAnalyse = document.querySelector("#analyze-btn");
const loader = document.querySelector("#loader");
const scoreYeux = document.querySelector("#score-eyes");
const scoreLevres = document.querySelector("#score-lips");
const scoreFinal = document.querySelector("#score-final");
const niveauSuspicion = document.querySelector("#suspicion-level");

formulaire.addEventListener("submit", async (event) => {
  event.preventDefault();
  await analyserVideo();
});

async function analyserVideo() {
  const fichierVideo = champVideo.files[0];

  if (!fichierVideo) {
    afficherErreur("Veuillez choisir une video avant de lancer l'analyse.");
    return;
  }

  const donnees = new FormData();
  donnees.append("video", fichierVideo);

  try {
    activerChargement(true);
    afficherMessage("Analyse en cours...");

    const reponse = await fetch(API_ANALYSE_URL, {
      method: "POST",
      body: donnees,
    });

    if (!reponse.ok) {
      throw new Error(`Erreur serveur ${reponse.status}`);
    }

    const resultat = await reponse.json();
    afficherResultats(resultat);
  } catch (erreur) {
    afficherErreur(`Impossible d'analyser la video. ${erreur.message}`);
  } finally {
    activerChargement(false);
  }
}

function activerChargement(estEnChargement) {
  boutonAnalyse.disabled = estEnChargement;
  champVideo.disabled = estEnChargement;
  boutonAnalyse.textContent = estEnChargement
    ? "Analyse en cours..."
    : "Lancer l'analyse";

  if (loader) {
    loader.classList.toggle("hidden", !estEnChargement);
  }
}

function afficherResultats(resultat) {
  scoreYeux.textContent = formaterScore(resultat.score_yeux);
  scoreLevres.textContent = formaterScore(resultat.score_levres);
  scoreFinal.textContent = formaterScore(resultat.score_final);
  niveauSuspicion.textContent = resultat.niveau ?? "Non disponible";

  if (resultat.message) {
    niveauSuspicion.title = resultat.message;
  }
}

function afficherMessage(message) {
  niveauSuspicion.textContent = message;
  niveauSuspicion.title = message;
}

function afficherErreur(message) {
  scoreYeux.textContent = "--";
  scoreLevres.textContent = "--";
  scoreFinal.textContent = "--";
  niveauSuspicion.textContent = message;
  niveauSuspicion.title = message;
}

function formaterScore(score) {
  if (score === undefined || score === null || Number.isNaN(Number(score))) {
    return "--";
  }

  const scoreNumerique = Number(score);
  const scorePourcentage = scoreNumerique <= 1 ? scoreNumerique * 100 : scoreNumerique;

  return `${Math.round(scorePourcentage)}%`;
}
