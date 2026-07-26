// Substitui o `globalCache` solto em nível de módulo (utils.js legado) por
// uma instância explícita, criada no composition root e injetada em quem
// precisa dela — em vez de estado mutável implícito compartilhado.
class CacheService {
  constructor() {
    this.store = new Map();
  }

  set(key, value) {
    this.store.set(key, value);
  }

  get(key) {
    return this.store.get(key);
  }
}

module.exports = CacheService;
