// Composition root: monta a aplicação Express, injeta dependências
// (conexão de banco, cache) nas rotas e registra o error handler central.
const express = require('express');
const { config } = require('./config');
const { createConnection, initSchema } = require('./config/database');
const CacheService = require('./services/cacheService');
const errorHandler = require('./middlewares/errorHandler');
const buildCheckoutRoutes = require('./routes/checkoutRoutes');
const buildReportRoutes = require('./routes/reportRoutes');
const buildUserRoutes = require('./routes/userRoutes');

async function createApp() {
  const app = express();
  app.use(express.json());

  const db = createConnection(':memory:');
  await initSchema(db);
  const cache = new CacheService();
  const deps = { db, cache };

  app.use('/api', buildCheckoutRoutes(deps));
  app.use('/api', buildReportRoutes(deps));
  app.use('/api', buildUserRoutes(deps));

  app.use(errorHandler);

  return app;
}

module.exports = createApp;
