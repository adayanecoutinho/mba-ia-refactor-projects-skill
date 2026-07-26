const express = require('express');
const checkoutController = require('../controllers/checkoutController');

function buildCheckoutRoutes(deps) {
  const router = express.Router();
  router.post('/checkout', (req, res, next) =>
    checkoutController.checkout(req, res, deps).catch(next)
  );
  return router;
}

module.exports = buildCheckoutRoutes;
