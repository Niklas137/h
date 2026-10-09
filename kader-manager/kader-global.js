/* Kader-Manager – Einstieg für Gastgeber ohne Modul-Import (z. B. React-App mit Content-Security-Policy ohne
   'unsafe-eval'): als <script type="module" src=".../kader-global.js"> laden, danach steht window.KaderTrikots
   mit kaderMounten, pruefen und ausLadoTeam bereit; das Ereignis "kader-trikots-bereit" meldet das Laden. */
import { kaderMounten } from './kader-einbettung.js';
import { pruefen, ausLadoTeam } from './kader-daten.js';
window.KaderTrikots = { kaderMounten, pruefen, ausLadoTeam };
window.dispatchEvent(new Event('kader-trikots-bereit'));
