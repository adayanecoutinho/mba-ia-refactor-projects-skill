// Usa o módulo nativo `node:sqlite` (Node >= 22.5, ainda experimental) em
// vez do pacote `sqlite3` do projeto legado. Isso elimina de uma vez: (1)
// a API baseada em callback que gerava o "callback hell" do AppManager.js
// original, e (2) a dependência de compilação nativa via node-gyp, que
// pode falhar em ambientes sandboxed sem acesso à internet completo.
//
// Nota de portabilidade: se o ambiente de execução usar Node < 22.5 (sem
// `node:sqlite`), troque este arquivo para usar `better-sqlite3` mantendo
// a mesma assinatura de `run/get/all` — o resto da aplicação não muda.
const { DatabaseSync } = require('node:sqlite');

function createConnection(path = ':memory:') {
  return new DatabaseSync(path);
}

function run(db, sql, params = []) {
  const result = db.prepare(sql).run(...params);
  return { lastID: Number(result.lastInsertRowid), changes: result.changes };
}

function get(db, sql, params = []) {
  return db.prepare(sql).get(...params);
}

function all(db, sql, params = []) {
  return db.prepare(sql).all(...params);
}

function initSchema(db) {
  db.exec('CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT, pass TEXT)');
  db.exec('CREATE TABLE courses (id INTEGER PRIMARY KEY, title TEXT, price REAL, active INTEGER)');
  db.exec('CREATE TABLE enrollments (id INTEGER PRIMARY KEY, user_id INTEGER, course_id INTEGER)');
  db.exec('CREATE TABLE payments (id INTEGER PRIMARY KEY, enrollment_id INTEGER, amount REAL, status TEXT)');
  db.exec('CREATE TABLE audit_logs (id INTEGER PRIMARY KEY, action TEXT, created_at DATETIME)');

  run(db, "INSERT INTO users (name, email, pass) VALUES ('Leonan', 'leonan@fullcycle.com.br', ?)", ['seed-hash-placeholder']);
  run(db, "INSERT INTO courses (title, price, active) VALUES ('Clean Architecture', 997.00, 1), ('Docker', 497.00, 1)");
  run(db, 'INSERT INTO enrollments (user_id, course_id) VALUES (1, 1)');
  run(db, "INSERT INTO payments (enrollment_id, amount, status) VALUES (1, 997.00, 'PAID')");
}

module.exports = { createConnection, run, get, all, initSchema };
