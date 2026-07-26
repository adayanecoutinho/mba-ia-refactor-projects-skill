const express = require('express');
const userController = require('../controllers/userController');

function buildUserRoutes(deps) {
  const router = express.Router();
  router.delete('/users/:id', (req, res, next) =>
    userController.deleteUser(req, res, deps).catch(next)
  );
  return router;
}

module.exports = buildUserRoutes;
