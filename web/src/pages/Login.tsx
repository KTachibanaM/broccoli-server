import React from 'react';
import {withRouter, RouteComponentProps, Redirect} from "react-router-dom";
import ApiClient from "../api/ApiClient";
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Container from '@material-ui/core/Container';
import {createStyles, Theme, withStyles, WithStyles} from "@material-ui/core";

const styles = (theme: Theme) => createStyles({
  paper: {
    marginTop: theme.spacing(8),
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  avatar: {
    margin: theme.spacing(1),
    backgroundColor: theme.palette.secondary.main,
  },
  form: {
    width: '100%', // Fix IE 11 issue.
    marginTop: theme.spacing(1),
  },
  submit: {
    margin: theme.spacing(3, 0, 2),
  },
});

type Props = RouteComponentProps & WithStyles<typeof styles> & {
  apiClient: ApiClient
}

interface State {
  loading: boolean,
  error?: string,
  username: string,
  password: string,
  redirectToReferrer: boolean
}

class Login extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      loading: false,
      username: '',
      password: '',
      redirectToReferrer: false
    }
  }

  login = (username: string, password: string) => {
    this.setState({
      loading: true,
      error: undefined
    });
    this.props.apiClient.auth(username, password)
      .then(authenticated => {
        if (authenticated) {
          this.setState({
            redirectToReferrer: true
          })
        } else {
          this.setState({
            error: "Unauthenticated"
          })
        }
      })
      .catch(error => {
        this.setState({ error: error.toString() })
      })
      .finally(() => {
        this.setState({
          loading: false
        })
      })
  };

  render() {
    if (this.state.redirectToReferrer) {
      const { from } = this.props.location.state || { from: { pathname: '/' } };
      return <Redirect to={from} />
    }

    const {classes} = this.props;
    return (
      <Container component="main" maxWidth="xs">
        <div className={classes.paper}>
          <form className={classes.form} noValidate>
            <TextField
              variant="outlined"
              margin="normal"
              required
              fullWidth
              id="username"
              label="Username"
              name="username"
              autoComplete="username"
              autoFocus
              value={this.state.username}
              onChange={e => {
                e.preventDefault();
                this.setState({
                  username: e.target.value
                })
              }}
              disabled={this.state.loading}
            />
            <TextField
              variant="outlined"
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              value={this.state.password}
              onChange={e => {
                e.preventDefault();
                this.setState({
                  password: e.target.value
                })
              }}
              disabled={this.state.loading}
            />
            {this.state.error ?
              <p style={{color: "red"}}>{this.state.error}</p> :
              null
            }
            <Button
              type="submit"
              fullWidth
              variant="contained"
              color="primary"
              className={classes.submit}
              onClick={e => {
                e.preventDefault();
                this.login(this.state.username, this.state.password)
              }}
              disabled={this.state.loading}
            >
              Log in
            </Button>
          </form>
        </div>
      </Container>
    )
  }
}

export default withStyles(styles)(withRouter(Login))
