const { run } = require('../config/database');

async function create(db, enrollmentId, amount, status) {
  const { lastID } = await run(
    db,
    'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
    [enrollmentId, amount, status]
  );
  return lastID;
}

module.exports = { create };
