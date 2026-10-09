/* Kader-Manager – Einstieg für index.html: hängt die Kaderseite in <main id="inhalt"> ein.
   Die eigentliche Logik steht in kader-einbettung.js (auch für die Einbettung in KFK LadoTeam). */
import { kaderMounten } from './kader-einbettung.js';
kaderMounten(document.getElementById('inhalt'));
