export function rosterPage(characters, filters, metrics, pageSize = 24) {
  const query = (filters.query || '').trim().toLowerCase();
  const rows = characters.filter(c => {
    const searchable = [c.name,c.race,c.specialty,c.series,...Object.keys(c.perks || {}),...(c.traits || [])].join(' ').toLowerCase();
    return (!query || searchable.includes(query)) && (!filters.status || c.status === filters.status)
      && (!filters.race || c.race === filters.race) && (!filters.kind || c.source_kind === filters.kind);
  });
  const ratings = new Map(rows.map(c => [c.id, metrics(c)]));
  rows.sort((a,b) => {
    if (filters.sort === 'con') return ratings.get(b.id).constitution - ratings.get(a.id).constitution || a.name.localeCompare(b.name);
    if (filters.sort === 'dps') return ratings.get(b.id).dps - ratings.get(a.id).dps || a.name.localeCompare(b.name);
    return a.name.localeCompare(b.name);
  });
  const pages = Math.max(1,Math.ceil(rows.length/pageSize));
  const page = Math.min(Math.max(0,filters.page || 0),pages-1);
  return {rows:rows.slice(page*pageSize,(page+1)*pageSize),total:rows.length,pages,page};
}
