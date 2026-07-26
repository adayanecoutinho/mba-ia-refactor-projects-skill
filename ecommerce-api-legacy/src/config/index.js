// Configuração centralizada. Nenhum segredo fica hardcoded aqui: tudo vem
// de variáveis de ambiente, com defaults seguros apenas para dev local.
require('dotenv').config();

const config = {
  port: parseInt(process.env.PORT || '3000', 10),
  dbUser: process.env.DB_USER || 'dev_user',
  dbPass: process.env.DB_PASS || 'dev-only-change-me',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || 'pk_test_dev_placeholder',
  smtpUser: process.env.SMTP_USER || 'no-reply@example.com',
};

const VALID_PAYMENT_STATUS = { PAID: 'PAID', DENIED: 'DENIED' };
const TEST_CARD_APPROVED_PREFIX = '4';

module.exports = { config, VALID_PAYMENT_STATUS, TEST_CARD_APPROVED_PREFIX };
