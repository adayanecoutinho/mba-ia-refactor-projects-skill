// Acesso a dados de usuários. Toda query é parametrizada.
const { run, get } = require('../config/database');

async function findByEmail(db, email) {
  return get(db, 'SELECT id, name, email, pass FROM users WHERE email = ?', [email]);
}

async function findById(db, id) {
  return get(db, 'SELECT id, name, email FROM users WHERE id = ?', [id]);
}

async function create(db, { name, email, passwordHash }) {
  const { lastID } = await run(
    db,
    'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
    [name, email, passwordHash]
  );
  return lastID;
}

async function remove(db, id) {
  return run(db, 'DELETE FROM users WHERE id = ?', [id]);
}

module.exports = { findByEmail, findById, create, remove };
