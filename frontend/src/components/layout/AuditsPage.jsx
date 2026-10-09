import { Typography, Box } from '@mui/material';
import AuditDataGrid from '../audits/AuditDataGrid.jsx'

function AuditsPage( { setNotification } ) {
  return (
    <>
        <Typography variant="h5"  gutterBottom>
          Audits
        </Typography>
        <Box sx={{ mb: 4}}>
          <AuditDataGrid onSuccess={setNotification}/>
        </Box>
    </>
  );
}

export default AuditsPage;