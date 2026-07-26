const express = require('express');
const reportController = require('../controllers/reportController');

function buildReportRoutes(deps) {
  const router = express.Router();
  router.get('/admin/financial-report', (req, res, next) =>
    reportController.financialReport(req, res, deps).catch(next)
  );
  return router;
}

module.exports = buildReportRoutes;
