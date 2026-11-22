function createAdminController(financialReportModel) {
    return {
        async financialReport(req, res) {
            const report = await financialReportModel.getReport();
            res.json(report);
        }
    };
}

module.exports = createAdminController;
