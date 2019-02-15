import React, {Component} from 'react';
import 'semantic-ui-css/semantic.min.css';
import {Container, Loader, Message, Grid, Image, Header, Menu, Button, Icon} from 'semantic-ui-react'
import ApiClient from './ApiClient'

class App extends Component {
  constructor(props) {
    super(props);
    this.apiClient = new ApiClient(
      process.env.REACT_APP_API_HOSTNAME,
      parseInt(process.env.REACT_APP_API_PORT),
      process.env.REACT_APP_S3_HOSTNAME,
      parseInt(process.env.REACT_APP_S3_PORT),
      process.env.REACT_APP_S3_BUCKET_NAME
    );

    this.state = {
      "loading": true,
      "data": [],
      "error": undefined
    }
  }

  componentDidMount() {
    this.loadNextPage()
  }

  loadNextPage() {
    window.scrollTo(0, 0);
    this.setState({
      "loading": true
    });
    const fromTimestamp = this.state.data.length !== 0
      ? this.state.data[this.state.data.length - 1]["created_at"] - 1
      : undefined;
    this.apiClient.nextPage(fromTimestamp)
      .then(data => {
        if (data !== null) {
          this.setState({
            "data": data
          })
        }
      })
      .catch(error => {
        this.setState({
          "error": error.toString()
        })
      })
      .finally(() => {
        this.setState({
          "loading": false
        })
      })
  }

  loadPrevPage() {
    window.scrollTo(0, 0);
    this.setState({
      "loading": true
    });
    const toTimestamp = this.state.data.length !== 0
      ? this.state.data[0]["created_at"] + 1
      : undefined;
    this.apiClient.prevPage(toTimestamp)
      .then(data => {
        if (data !== null) {
          this.setState({
            "data": data
          })
        }
      })
      .catch(error => {
        this.setState({
          "error": error.toString()
        })
      })
      .finally(() => {
        this.setState({
          "loading": false
        })
      })
  }

  renderImageRow(items, rowKey) {
    const columnCount = this.props.columnCount;
    const columnComponents = [];
    for (let columnI = 0; columnI < items.length; ++columnI) {
      columnComponents.push((
        <Grid.Column key={columnI}>
          <Image
            src={items[columnI]["s3_image_link"]}
            size='medium'
            as='a'
            href={items[columnI]["source"]}
            target='_blank'
          />
        </Grid.Column>
      ))
    }
    return (
      <Grid relaxed columns={columnCount} key={rowKey}>
        {columnComponents}
      </Grid>
    )
  }

  renderImageGrid() {
    const currentPageData = this.state.data;
    const totalCount = currentPageData.length;
    if (totalCount === 0) {
      return (<Header as='h3'>No images ¯\_(ツ)_/¯</Header>)
    }
    const columnCount = this.props.columnCount;
    const fullRowCount = Math.floor(totalCount / columnCount);
    const remainderColumnCount = totalCount % columnCount;
    const rowComponents = [];
    for (let rowI = 0; rowI < fullRowCount; ++rowI) {
      rowComponents.push(
        this.renderImageRow(currentPageData.slice(rowI * columnCount, (rowI + 1) * columnCount), rowI)
      )
    }
    if (remainderColumnCount !== 0) {
      rowComponents.push(
        this.renderImageRow(currentPageData.slice(fullRowCount * columnCount, currentPageData.length), fullRowCount)
      );
    }
    return rowComponents
  }

  renderNavigationButtons() {
    return (
      <Menu inverted>
        <Button.Group fluid>
          <Button icon inverted onClick={() => {this.loadPrevPage()}}>
            <Icon name='arrow left'/>
          </Button>
          <Button.Or text='o' />
          <Button icon inverted onClick={() => {this.loadNextPage()}}>
            <Icon name='arrow right'/>
          </Button>
        </Button.Group>
      </Menu>
    )
  }

  renderStream() {
    if (this.state.loading) {
      return (<Loader inverted>Loading</Loader>)
    }
    if (this.state.error) {
      return (
        <Message negative>
          <Message.Header>Ooops</Message.Header>
          <p>{this.state.error}</p>
        </Message>
      )
    }
    return (
      <Container>
        {this.renderNavigationButtons()}
        {this.renderImageGrid()}
        {this.renderNavigationButtons()}
      </Container>
    )
  }

  render() {
    return (
      <Container>
        <Menu inverted>
          <Menu.Item header>Herr あし</Menu.Item>
          <Menu.Item name='Stream'/>
          <Menu.Item name='Random'/>
        </Menu>
        {this.renderStream()}
      </Container>
    );
  }
}

export default App;
