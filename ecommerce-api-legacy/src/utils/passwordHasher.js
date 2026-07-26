// Substitui a função `badCrypto` do utils.js legado (que só embaralhava
// base64 em loop — não é hashing criptográfico algum e é trivialmente
// reversível) por bcrypt, que é o padrão atual recomendado para senha.
const bcrypt = require('bcryptjs');

const SALT_ROUNDS = 10;

async function hash(plainPassword) {
  return bcrypt.hash(plainPassword, SALT_ROUNDS);
}

async function compare(plainPassword, passwordHash) {
  return bcrypt.compare(plainPassword, passwordHash);
}

module.exports = { hash, compare };
