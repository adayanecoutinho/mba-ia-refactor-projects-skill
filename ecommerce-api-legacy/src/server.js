const createApp = require('./app');
const { config } = require('./config');

createApp()
  .then((app) => {
    app.listen(config.port, () => {
      console.log(`API rodando na porta ${config.port}...`);
    });
  })
  .catch((err) => {
    console.error('Falha ao iniciar a aplicação:', err);
    process.exit(1);
  });
