const API_ANALYSE_URL = "http://127.0.0.1:8000/api/v1/deepfake/analyser-video";
const API_HEALTH_URL = "http://127.0.0.1:8000/api/v1/health";

const formulaire = document.querySelector("#upload-form");
const champVideo = document.querySelector("#video-upload");
const boutonAnalyse = document.querySelector("#analyze-btn");
const apiStatus = document.querySelector("#api-status");
const selectedFile = document.querySelector("#selected-file");
const scoreYeux = document.querySelector("#score-eyes");
const scoreLevres = document.querySelector("#score-lips");
const scoreFinal = document.querySelector("#score-final");
const niveauSuspicion = document.querySelector("#suspicion-level");
const verdictMessage = document.querySelector("#verdict-message");
const verdictCard = document.querySelector("#verdict-card");
const eyesDetail = document.querySelector("#eyes-detail");
const lipsDetail = document.querySelector("#lips-detail");
const finalDetail = document.querySelector("#final-detail");
const metaFilename = document.querySelector("#meta-filename");
const metaSize = document.querySelector("#meta-size");
const metaStatus = document.querySelector("#meta-status");

const statusUpload = document.querySelector("#status-upload");
const statusAnalysis = document.querySelector("#status-analysis");
const statusCleanup = document.querySelector("#status-cleanup");

verifierApi();

champVideo.addEventListener("change", () => {
  const fichier = champVideo.files[0];
  selectedFile.textContent = fichier ? fichier.name : "Choisir une video";
  metaFilename.textContent = fichier ? fichier.name : "--";
  metaSize.textContent = fichier ? formaterTaille(fichier.size) : "--";
  definirStatut(statusUpload, fichier ? "active" : "", fichier ? "Video prete a envoyer" : "Video non envoyee");
});

formulaire.addEventListener("submit", async (event) => {
  event.preventDefault();
  await analyserVideo();
});

async function verifierApi() {
  try {
    const reponse = await fetch(API_HEALTH_URL);
    apiStatus.textContent = reponse.ok ? "API active" : "API indisponible";
    apiStatus.style.color = reponse.ok ? "var(--green)" : "var(--red)";
  } catch {
    apiStatus.textContent = "API hors ligne";
    apiStatus.style.color = "var(--red)";
  }
}

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
    definirStatut(statusUpload, "active", "Envoi de la video au backend...");
    definirStatut(statusAnalysis, "active", "Analyse en cours...");
    definirStatut(statusCleanup, "", "Nettoyage en attente");
    afficherMessage("Analyse en cours", "La video est envoyee puis analysee par les modules yeux et levres.");

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
  boutonAnalyse.textContent = estEnChargement ? "Analyse en cours..." : "Analyser";
}

function afficherResultats(resultat) {
  const niveau = (resultat.niveau || "non disponible").toLowerCase();
  const detailsYeux = resultat.details?.yeux || {};
  const detailsLevres = resultat.details?.levres || {};

  scoreYeux.textContent = formaterScore(resultat.score_yeux);
  scoreLevres.textContent = formaterScore(resultat.score_levres);
  scoreFinal.textContent = formaterScore(resultat.score_final);
  niveauSuspicion.textContent = normaliserNiveau(resultat.niveau);
  verdictMessage.textContent = resultat.message || "Analyse terminee.";

  eyesDetail.textContent = detailsYeux.message || "Score base sur le module de clignements.";
  lipsDetail.textContent = detailsLevres.message || "Score base sur le module de synchronisation labiale.";
  finalDetail.textContent = resultat.details?.interpretation || "Score combine des modules disponibles.";

  metaFilename.textContent = resultat.upload?.nom_original || resultat.filename || "--";
  metaSize.textContent = resultat.upload?.taille_octets ? formaterTaille(resultat.upload.taille_octets) : "--";
  metaStatus.textContent = resultat.statut || "termine";

  verdictCard.className = `verdict-card ${niveau}`;
  definirStatut(statusUpload, "done", "Video recue par le backend");
  definirStatut(statusAnalysis, resultat.statut === "erreur" ? "error" : "done", resultat.message || "Analyse terminee");

  const fichierSupprime = resultat.upload?.fichier_temporaire_supprime;
  definirStatut(
    statusCleanup,
    fichierSupprime ? "done" : "active",
    fichierSupprime ? "Fichier temporaire supprime" : "Fichier temporaire non confirme"
  );
}

function afficherMessage(titre, message) {
  niveauSuspicion.textContent = titre;
  verdictMessage.textContent = message;
  verdictCard.className = "verdict-card";
}

function afficherErreur(message) {
  scoreYeux.textContent = "--";
  scoreLevres.textContent = "--";
  scoreFinal.textContent = "--";
  niveauSuspicion.textContent = "Erreur";
  verdictMessage.textContent = message;
  metaStatus.textContent = "erreur";
  verdictCard.className = "verdict-card erreur";
  definirStatut(statusUpload, "error", "Erreur pendant l'envoi ou l'analyse");
  definirStatut(statusAnalysis, "error", message);
}

function definirStatut(element, etat, texte) {
  element.className = `status-item ${etat}`.trim();
  element.querySelector("p").textContent = texte;
}

function formaterScore(score) {
  if (score === undefined || score === null || Number.isNaN(Number(score))) {
    return "--";
  }

  return `${Math.round(Number(score))}%`;
}

function formaterTaille(octets) {
  if (!octets) {
    return "--";
  }

  if (octets < 1024 * 1024) {
    return `${Math.round(octets / 1024)} Ko`;
  }

  return `${(octets / (1024 * 1024)).toFixed(2)} Mo`;
}

function normaliserNiveau(niveau) {
  if (!niveau) {
    return "Non disponible";
  }

  return niveau.charAt(0).toUpperCase() + niveau.slice(1);
}
