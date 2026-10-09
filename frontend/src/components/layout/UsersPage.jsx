import { Typography, Box } from '@mui/material';
import UserDataGrid from '../users/UserDataGrid';

function UsersPage( { setNotification } ) {
  return (
    <>
        <Typography variant="h5"  gutterBottom>
          Users
        </Typography>
        <Box sx={{ mb: 4}}>
          <UserDataGrid onSuccess={setNotification}/>
        </Box>
    </>
  );
}

export default UsersPage;