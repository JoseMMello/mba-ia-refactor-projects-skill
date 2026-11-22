const { PAYMENT_STATUS } = require('../models/paymentStatus');

const APPROVED_CARD_PREFIX = '4';

function createPaymentService({ gatewayKey, logger }) {
    return {
        // Returns the payment status for the card. The card number is never logged.
        authorize(card) {
            logger.debug(`Processando pagamento (chave do gateway configurada: ${Boolean(gatewayKey)})`);
            return card.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
        }
    };
}

module.exports = createPaymentService;
