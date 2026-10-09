import { Typography, Box } from '@mui/material';
import FieldJobDataGrid from '../field_jobs/FieldJobDataGrid.jsx';

function FieldJobsPage( { setNotification } ) {
  return (
    <>
        <Typography variant="h5"  gutterBottom>
          Field Jobs
        </Typography>
        <Box sx={{ mb: 4}}>
          <FieldJobDataGrid onSuccess={setNotification}/>
        </Box>
    </>
  );
}

export default FieldJobsPage;