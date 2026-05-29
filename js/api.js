/**
 * StageFlow — api.js
 * Client JavaScript centralisé pour communiquer avec le backend Django.
 * Toutes les pages frontend importent ce fichier via <script src="js/api.js"></script>.
 * 
 * EN MODE DEV (sans serveur Django actif), les fonctions retournent des données
 * fictives (mock) pour que l'interface reste fonctionnelle.
 */

// ─────────────────────────────────────────────────────────────────────────────
// CONFIGURATION
// ─────────────────────────────────────────────────────────────────────────────

const API_BASE = 'http://127.0.0.1:8000/api';

// Récupère l'utilisateur depuis sessionStorage (sauvegardé après connexion)
function getCurrentUser() {
  try {
    return JSON.parse(sessionStorage.getItem('stageflow_user')) || null;
  } catch (e) {
    return null;
  }
}

function saveCurrentUser(user) {
  sessionStorage.setItem('stageflow_user', JSON.stringify(user));
}

function logout() {
  sessionStorage.removeItem('stageflow_user');
  window.location.href = 'connexion.html';
}

// ─────────────────────────────────────────────────────────────────────────────
// HELPER : requête JSON vers le backend Django
// ─────────────────────────────────────────────────────────────────────────────

async function apiRequest(method, endpoint, body = null) {
  try {
    const options = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    if (body && method !== 'GET') {
      options.body = JSON.stringify(body);
    }
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    const data = await res.json();
    return { ok: res.ok, status: res.status, data };
  } catch (err) {
    console.warn('[StageFlow API] Backend inaccessible – mode démonstration activé.', err);
    return { ok: false, status: 0, data: null, offline: true };
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// 1. AUTHENTIFICATION
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Connecte un utilisateur par son email institutionnel.
 * @param {string} email  Ex: "a.ouali@estin.dz"
 * @returns {Object}      { success, user, error }
 */
async function apiLogin(email) {
  const result = await apiRequest('POST', '/login/', { email });

  if (result.offline || !result.ok) {
    // Données de démo si le backend n'est pas disponible
    const demoUsers = {
      'a.ouali@estin.dz':    { id: 1, nom: 'Ouali', prenom: 'Amina',  email, role: 'etudiant' },
      'a.benali@estin.dz':   { id: 2, nom: 'Benali', prenom: 'Ahmed', email, role: 'enseignant' },
      'admin@estin.dz':      { id: 3, nom: 'Admin',  prenom: 'DPGR',  email, role: 'admin' },
    };
    const demoUser = demoUsers[email.toLowerCase()];
    if (demoUser) {
      saveCurrentUser(demoUser);
      return { success: true, user: demoUser, demo: true };
    }
    return { success: false, error: 'Email introuvable (mode démo : utilisez a.ouali@estin.dz)' };
  }

  if (result.data.success) {
    saveCurrentUser(result.data.user);
    return { success: true, user: result.data.user };
  }
  return { success: false, error: result.data.error };
}

// ─────────────────────────────────────────────────────────────────────────────
// 2. PROPOSITIONS DE STAGE
// ─────────────────────────────────────────────────────────────────────────────

const MOCK_PROPOSITIONS = [
  {
    id: 1,
    titre: 'Application de gestion des ressources humaines',
    description: 'Conception et développement d\'une application web full-stack moderne avec React et Node.js.',
    technologies: 'React, Node.js, MongoDB',
    entreprise: 'Sonatrach',
    statut: 'Ouverte',
    date_publication: '2026-03-01',
    enseignant: { id: 2, nom: 'Mansouri', prenom: 'Brahim' }
  },
  {
    id: 2,
    titre: 'Analyse prédictive des données médicales',
    description: 'Étude et modélisation prédictive sur des jeux de données médicaux avec Python.',
    technologies: 'Python, Pandas, scikit-learn',
    entreprise: 'CHU Béjaïa',
    statut: 'Ouverte',
    date_publication: '2026-03-05',
    enseignant: { id: 3, nom: 'Meziane', prenom: 'Sara' }
  },
  {
    id: 3,
    titre: 'Audit de sécurité et tests d\'intrusion',
    description: 'Réaliser un audit complet de sécurité d\'un système d\'information en entreprise.',
    technologies: 'Kali Linux, Metasploit, Nmap',
    entreprise: 'BNA Banque',
    statut: 'Ouverte',
    date_publication: '2026-03-10',
    enseignant: { id: 4, nom: 'Zerrouk', prenom: 'Ahmed' }
  },
  {
    id: 4,
    titre: 'Chatbot NLP pour service client automatisé',
    description: 'Conception d\'un assistant conversationnel intelligent avec transformers et LLMs.',
    technologies: 'Python, HuggingFace, LangChain',
    entreprise: 'Djezzy',
    statut: 'Ouverte',
    date_publication: '2026-03-15',
    enseignant: { id: 5, nom: 'Bouchenak', prenom: 'Nadia' }
  }
];

/**
 * Récupère toutes les propositions de stage disponibles.
 * @returns {Array} Liste des propositions
 */
async function apiGetPropositions() {
  const result = await apiRequest('GET', '/propositions/');
  if (result.ok && result.data?.propositions) {
    return result.data.propositions;
  }
  return MOCK_PROPOSITIONS;
}

/**
 * Crée une nouvelle proposition (côté enseignant).
 * @param {Object} payload { id_enseignant, titre, description, technologies, entreprise }
 * @returns {Object} { success, id_proposition, message }
 */
async function apiCreateProposition(payload) {
  const result = await apiRequest('POST', '/propositions/', payload);
  if (result.ok) return result.data;
  return { success: true, id_proposition: Date.now(), message: 'Proposition créée (démo).' };
}

// ─────────────────────────────────────────────────────────────────────────────
// 3. DEMANDES DE STAGE
// ─────────────────────────────────────────────────────────────────────────────

const MOCK_DEMANDES = [
  {
    id: 1,
    date_demande: '2026-03-25',
    statut: 'Acceptée',
    lettre_motivation: '...',
    etudiant: { id: 1, nom: 'Ouali', prenom: 'Amina', matricule: '20220345', specialite: 'Cybersécurité' },
    proposition: { id: 1, titre: 'Développement web', entreprise: 'Sonatrach' },
    motif_refus: null,
    attestation_numero: null
  },
  {
    id: 2,
    date_demande: '2026-03-08',
    statut: 'Refusée',
    lettre_motivation: '...',
    etudiant: { id: 1, nom: 'Ouali', prenom: 'Amina', matricule: '20220345', specialite: 'Cybersécurité' },
    proposition: { id: 2, titre: 'Data Science', entreprise: 'CHU Béjaïa' },
    motif_refus: 'Profil ne correspond pas aux prérequis.',
    attestation_numero: null
  }
];

/**
 * Récupère les demandes d'un étudiant ou d'un enseignant.
 * @param {Object} params { id_etudiant? | id_enseignant? }
 * @returns {Array} Liste des demandes
 */
async function apiGetDemandes(params = {}) {
  const qs = new URLSearchParams(params).toString();
  const result = await apiRequest('GET', `/demandes/?${qs}`);
  if (result.ok && result.data?.demandes) return result.data.demandes;
  return MOCK_DEMANDES;
}

/**
 * Soumet une candidature de stage (étudiant).
 * @param {Object} payload { id_etudiant, id_proposition, lettre_motivation }
 * @returns {Object} { success, id_demande, message }
 */
async function apiSoumettreDemande(payload) {
  const result = await apiRequest('POST', '/demandes/', payload);
  if (result.ok) return result.data;
  return { success: true, id_demande: Date.now(), message: 'Candidature soumise (démo).' };
}

/**
 * Traite une demande (accepter, refuser, valider, archiver).
 * @param {number} idDemande
 * @param {Object} payload { statut: 'Acceptée'|'Refusée'|'Validée'|'Archivée', motif?, mention?, appreciation? }
 */
async function apiTraiterDemande(idDemande, payload) {
  const result = await apiRequest('POST', `/demandes/${idDemande}/traitement/`, payload);
  if (result.ok) return result.data;
  return { success: true, nouveau_statut: payload.statut, message: 'Statut mis à jour (démo).' };
}

// ─────────────────────────────────────────────────────────────────────────────
// 4. NOTIFICATIONS
// ─────────────────────────────────────────────────────────────────────────────

const MOCK_NOTIFICATIONS = [
  {
    id: 1, lu: false, date_envoi: '2026-04-12T16:10:00',
    message: 'Votre demande pour le stage Développement web a été validée par l\'enseignant.'
  },
  {
    id: 2, lu: false, date_envoi: '2026-04-11T14:30:00',
    message: 'Félicitations ! Votre candidature pour le stage Application RH a été acceptée.'
  },
  {
    id: 3, lu: true, date_envoi: '2026-04-09T10:05:00',
    message: 'Votre candidature pour le stage Data Science a été refusée.'
  }
];

/**
 * Récupère les notifications d'un utilisateur.
 * @param {number} idUser
 * @returns {Array} Liste des notifications
 */
async function apiGetNotifications(idUser) {
  const result = await apiRequest('GET', `/notifications/?id_user=${idUser}`);
  if (result.ok && result.data?.notifications) return result.data.notifications;
  return MOCK_NOTIFICATIONS;
}

/**
 * Marque toutes les notifications d'un utilisateur comme lues.
 * @param {number} idUser
 */
async function apiMarquerNotificationsLues(idUser) {
  const result = await apiRequest('POST', '/notifications/', { id_user: idUser });
  return result.ok ? result.data : { success: true };
}

// ─────────────────────────────────────────────────────────────────────────────
// 5. UTILITAIRES UI
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Affiche un toast (notification visuelle) en bas à droite de l'écran.
 * Compatible avec tous les dashboards StageFlow.
 * @param {string} msg  Message à afficher
 * @param {'info'|'success'|'error'} type
 */
function sfToast(msg, type = 'info') {
  let el = document.getElementById('sf-toast');
  if (!el) {
    el = document.createElement('div');
    el.id = 'sf-toast';
    el.style.cssText = `
      position:fixed;bottom:24px;right:24px;
      border-radius:12px;padding:13px 20px;
      font-size:13px;font-weight:500;
      box-shadow:0 8px 32px rgba(30,58,110,0.18);
      transform:translateY(80px);opacity:0;
      transition:all .3s;z-index:9999;max-width:320px;
      font-family:'Plus Jakarta Sans',sans-serif;
    `;
    document.body.appendChild(el);
  }
  const colors = {
    info:    { bg: '#1e3a6e', fg: '#fff' },
    success: { bg: '#065f46', fg: '#fff' },
    error:   { bg: '#991b1b', fg: '#fff' },
  };
  const c = colors[type] || colors.info;
  el.style.background = c.bg;
  el.style.color = c.fg;
  el.textContent = msg;
  el.style.transform = 'translateY(0)';
  el.style.opacity = '1';

  clearTimeout(el._timer);
  el._timer = setTimeout(() => {
    el.style.transform = 'translateY(80px)';
    el.style.opacity = '0';
  }, 3500);
}

/**
 * Retourne le badge HTML coloré selon le statut d'une demande.
 * @param {string} statut
 * @returns {string} HTML du badge
 */
function sfStatusBadge(statut) {
  const map = {
    'En attente': '<span class="badge b-orange">● En attente</span>',
    'Acceptée':   '<span class="badge b-green">✓ Acceptée</span>',
    'Refusée':    '<span class="badge b-red">✗ Refusée</span>',
    'Validée':    '<span class="badge b-blue">★ Validée</span>',
    'Archivée':   '<span class="badge b-orange">📁 Archivée</span>',
  };
  return map[statut] || `<span class="badge">${statut}</span>`;
}

/**
 * Formate une date ISO en date française lisible.
 * @param {string} isoDate  Ex: "2026-03-25T10:00:00"
 * @returns {string}        Ex: "25 Mars 2026"
 */
function sfFormatDate(isoDate) {
  if (!isoDate) return '—';
  const months = ['Janvier','Février','Mars','Avril','Mai','Juin',
                  'Juillet','Août','Septembre','Octobre','Novembre','Décembre'];
  const d = new Date(isoDate);
  return `${d.getDate()} ${months[d.getMonth()]} ${d.getFullYear()}`;
}

/**
 * Redirige vers la bonne page dashboard selon le rôle de l'utilisateur.
 * @param {Object} user
 */
function sfRedirectByRole(user) {
  const routes = {
    etudiant:    'etudiant.html',
    enseignant:  'enseignant.html',
    admin:       'admin.html',
  };
  window.location.href = routes[user.role] || 'connexion.html';
}

// Auto-init : vérifie si l'utilisateur est connecté sur les pages protégées
(function() {
  const publicPages = ['connexion.html', 'acceuil.html', 'index.html'];
  const currentPage = window.location.pathname.split('/').pop();
  if (!publicPages.includes(currentPage)) {
    const user = getCurrentUser();
    if (!user) {
      window.location.href = 'connexion.html';
    }
  }
})();
