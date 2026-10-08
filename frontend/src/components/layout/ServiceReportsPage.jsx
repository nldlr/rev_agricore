import { Typography, Box } from '@mui/material';
import ServiceReportDataGrid from '../service_reports/ServiceReportDataGrid.jsx';

function ServiceReportsPage( { setNotification } ) {
  return (
    <>
        <Typography variant="h5" component="h2" gutterBottom>
          Service Reports
        </Typography>
        <Box sx={{ mb: 4}}>
          <ServiceReportDataGrid onSuccess={setNotification}/>
        </Box>
    </>
  );
}

export default ServiceReportsPage;