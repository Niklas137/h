/* KFK LadoTeam – öffentliche, nur lesende Kader-Schnittstelle für die Trikot-Animation.
   Neue Datei, keine bestehende Datei der App wird verändert. Ablage: app/api/public/kader/route.ts

   Liefert ohne Anmeldung ausschließlich: id, name, nameUk, nameUkConfirmed, position, detail,
   white, black, status, teamRole. Keine E-Mails, Notizen, Mitglieder, Termine, Finanzen oder Nachrichten.
   Deaktivierte Spieler (status "inactive") werden nicht ausgegeben.

   ERLAUBTE_HERKUNFT: Domains, die die Schnittstelle aus dem Browser abrufen dürfen (CORS), z. B. die
   KFK-Website. Ohne passende Herkunft wird die Antwort zwar geliefert, der Browser einer fremden Seite
   darf sie aber nicht lesen. Für den Test im eigenen Browser oder per curl ist keine Herkunft nötig. */
import {loadTeam} from '../../../../lib/server';

export const dynamic = 'force-dynamic';

const ERLAUBTE_HERKUNFT: string[] = [
  // 'https://www.kfk-ladoteam.example',   // KFK-Website hier eintragen (Schema + Host, ohne Pfad)
];

function kopfzeilen(request: Request) {
  const herkunft = request.headers.get('origin') || '';
  const h: Record<string, string> = {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'public, max-age=60',
    'X-Content-Type-Options': 'nosniff',
  };
  if (herkunft && ERLAUBTE_HERKUNFT.includes(herkunft)) {
    h['Access-Control-Allow-Origin'] = herkunft;
    h['Vary'] = 'Origin';
  }
  return h;
}

export async function OPTIONS(request: Request) {
  const h = kopfzeilen(request);
  h['Access-Control-Allow-Methods'] = 'GET, OPTIONS';
  h['Access-Control-Max-Age'] = '600';
  return new Response(null, {status: 204, headers: h});
}

export async function GET(request: Request) {
  const h = kopfzeilen(request);
  try {
    const {state, revision} = await loadTeam();
    const players = state.players
      .filter(p => p.status !== 'inactive')
      .map(p => ({
        id: p.id,
        name: p.name,
        nameUk: p.nameUk || '',
        nameUkConfirmed: !!p.nameUkConfirmed,
        position: p.position,
        detail: p.detail || '',
        white: p.white || '',
        black: p.black || '',
        status: p.status,
        teamRole: p.teamRole || '',
      }));
    const body = {
      format: 'kfk-kader',
      version: 1,
      revision,
      exportedAt: new Date().toISOString(),
      team: {name: state.settings.teamName},
      players,
    };
    return new Response(JSON.stringify(body), {headers: h});
  } catch {
    return new Response(JSON.stringify({error: 'unavailable'}), {status: 503, headers: {...h, 'Cache-Control': 'no-store'}});
  }
}
