const courseModel = require('../models/courseModel');
const enrollmentModel = require('../models/enrollmentModel');

async function financialReport(req, res, { db }) {
  const courses = await courseModel.findAll(db);

  const report = await Promise.all(
    courses.map(async (course) => {
      const rows = await enrollmentModel.findWithUserAndPaymentByCourse(db, course.id);
      const revenue = rows.reduce(
        (sum, row) => (row.payment_status === 'PAID' ? sum + row.paid_amount : sum),
        0
      );
      const students = rows.map((row) => ({
        student: row.student_name || 'Unknown',
        paid: row.paid_amount || 0,
      }));
      return { course: course.title, revenue, students };
    })
  );

  return res.json(report);
}

module.exports = { financialReport };
