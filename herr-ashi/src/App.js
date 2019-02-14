import React, { Component } from 'react';
import 'semantic-ui-css/semantic.min.css';
import { Container, Loader, Message, Grid, Image, Header } from 'semantic-ui-react'
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
    this.apiClient.nextPage()
      .then(data => {
        this.setState({
          "data": data
        })
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
          <Image src={items[columnI]["s3_image_link"]} />
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

  renderPage() {
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
    return <div>{this.renderImageGrid()}</div>
  }

  render() {
    return (
      <Container>
        {this.renderPage()}
      </Container>
    );
  }
}

export default App;
