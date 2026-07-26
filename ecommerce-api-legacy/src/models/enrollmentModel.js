const { run, all } = require('../config/database');

async function create(db, userId, courseId) {
  const { lastID } = await run(
    db,
    'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
    [userId, courseId]
  );
  return lastID;
}

// Relatório financeiro resolvido com uma única query (JOIN) em vez do N+1
// (1 query de enrollments + 1 de usuário + 1 de pagamento por matrícula)
// do código legado.
async function findWithUserAndPaymentByCourse(db, courseId) {
  return all(
    db,
    `SELECT e.id AS enrollment_id, u.name AS student_name,
            p.amount AS paid_amount, p.status AS payment_status
     FROM enrollments e
     LEFT JOIN users u ON u.id = e.user_id
     LEFT JOIN payments p ON p.enrollment_id = e.id
     WHERE e.course_id = ?`,
    [courseId]
  );
}

module.exports = { create, findWithUserAndPaymentByCourse };
