output "cluster_name" {
  value = aws_eks_cluster.k8s.name
}

output "cluster_endpoint" {
  value = aws_eks_cluster.k8s.endpoint
}

output "cluster_certificate_authority" {
  value = aws_eks_cluster.k8s.certificate_authority[0].data
}
